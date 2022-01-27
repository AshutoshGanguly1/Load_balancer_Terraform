import os
import re
import subprocess
from datetime import datetime, timedelta
import json
import sys
import re
import time


tags = ["instance-pod"]
threshold_cpu_usage =  20
executable_shell_script = ".././execute_flow_single.sh"
instance_dict = {"name":[],"instance_id":[],"publicip":[], "privateip":[]}

def create_instance(instance_type):

    instance_id = ''
    public_ip = ''
    private_ip = ''
    date = datetime.now().strftime("%Y-%m-%d-%I%M%S%p")
    name = "instance-pod{}".format(date)
    security_groups = ["${aws_security_group.terraformsg.name}"]
    key_name = "terraform_keypair"
    type = '{' + ' \n ami = "ami-0fb653ca2d3203ac1" \n instance_type = "{}"'.format(instance_type) +' \n security_groups = ["${aws_security_group.terraformsg.name}"]' + '\n key_name = "terraform_keypair"'
    tags1 = '\n tags = {\n '
    tags2 = 'Name = "{}" '.format(name)
    tags3 = '\n  }\n }'
    resource_block = '\n resource "aws_instance" "{}" {} {} {} {}'.format(name,type,tags1,tags2,tags3)
    with open('terraform.tf','a') as f:
        f.write(resource_block)
    f.close()

    command1 ='terraform apply -auto-approve -lock="false"'
    subprocess.run([command1], shell = True)
#make the instance_dict
    f = open("terraform.tfstate", "r")
    data = json.load(f)
    for i in range(len(data['resources'])):
         name_i = data['resources'][i]['name']
         if name_i == name:
             instance_id = data['resources'][i]['instances'][0]['attributes']['id']
             public_ip = data['resources'][i]['instances'][0]['attributes']['public_ip']
             private_ip = data['resources'][i]['instances'][0]['attributes']['private_ip']

    instance_dict["name"].append(name)
    instance_dict["instance_id"].append(instance_id)
    instance_dict["publicip"].append(public_ip)
    instance_dict["privateip"].append(private_ip)
#write intance_dict to instance_details.json
    with open('instance_details.json','r+') as file:

        file_data = json.load(file)

        file_data["instance_details"].append(instance_dict)
        file.seek(0)
        json.dump(file_data, file, indent = 4)
        file.close()

    return instance_id

def terminate_instance(instance_id):
    name = ''
    flag = False

    f = open('instance_details.json', 'r')
    data = json.load(f)

    for i in range(0,len(data['instance_details'])):

        id = data['instance_details'][i]['instance_id'][0]
        if id == instance_id:
            name = data['instance_details'][i]['name'][0]
            del (data['instance_details'][i])
            break
    with open('instance_details.json', 'w') as f:
        f.seek(0)
        json.dump(data, f, indent = 4)

    f.close()

    f = open('terraform.tf', 'r')
    string = f.read()
    f.close()
   #split the file using the line 'resource "aws_instance" "{}"'
    tmp = string.split('resource "aws_instance" "{}"'.format(name))
    string1 = tmp[0]
    #we split the next by a closed curly bracket
    tmp2 = tmp[1].split('{',1)
    tmp3 = tmp2[1].split('}',1)
    tmp4 = tmp3[1].split('}',1)
    tmp5 = tmp4[1].split('}',1)
    #print(string1)
    #print(tmp5[1])
    file = string1 + tmp5[1]
    with open('terraform.tf','w') as f:
            f.write(file)
    f.close()
    command2 = 'terraform apply -auto-approve -lock="false"'
    subprocess.run([command2], shell = True)

 #Check for success status
    subprocess.run(["terraform state list >> state_list.txt"], shell =True)
    f = open("state_list.txt", "r")
    if not name in f:
 #print("successfully deleted: {}".format(resource_type_name))
        flag = True
    else:
        print("Not deleted")
    os.remove("state_list.txt")
    return flag


def execute_commands(instance_id, dict_attributes):
    publicip = ''

    f = open('instance_details.json', 'r')
    data = json.load(f)
    for i in range(len(data['instance_details'])):
        id = data['instance_details'][i]['instance_id'][0]
        if id == instance_id:
            publicip = data['instance_details'][i]['publicip'][0]
    f.close()
    command_initial = "ssh -o StrictHostKeyChecking=no -i newkey1.pem ubuntu@{} exit".format(publicip)
    command3 = "scp -o StrictHostKeyChecking=no -i newkey1.pem {} ubuntu@{}:/home/ubuntu/".format(executable_shell_script,publicip)
    command_new = "ssh -o StrictHostKeyChecking=no -i newkey1.pem ubuntu@{} chmod u+x execute_flow_single.sh".format(publicip)
    command4 = "ssh -o StrictHostKeyChecking=no -i newkey1.pem ubuntu@{} ./execute_flow_single.sh {} {} {} {}".format(publicip,dict_attributes[1],dict_attributes[2],dict_attributes[3],dict_attributes[4])
    print(command3)
    print(command4)
    subprocess.run([command_initial], shell=True)
    subprocess.run([command3], shell=True)
    subprocess.run([command_new], shell=True)
    subprocess.run([command4], shell=True)
    #print('abc123')

    return True

def list_process_in_instance(instance_id):
    publicip = ''
    f = open('instance_details.json', 'r')
    data = json.load(f)
    for i in range(len(data['instance_details'])):
        id = data['instance_details'][i]['instance_id'][0]
        if id == instance_id:
            publicip = data['instance_details'][i]['publicip'][0]
    f.close()
    list_process = []
    shell_command = "ps aux | grep execute_flow_single.sh"
    command5 = "ssh -o StrictHostKeyChecking=no -i newkey1.pem ubuntu@{} {} > list_process.txt".format(publicip,shell_command)
    subprocess.run([command5], shell=True)

    f = open("list_process.txt", "r")
    for items in f:
        list_process.append(items)
    os.remove('list_process.txt')
    print(list_process)
    return list_process

def check_docker_running(instance_id):
    list_process = list_process_in_instance(instance_id)
    print(list_process)
    print(len(list_process))
    if len(list_process) > 0:
        return True
    else:
        return False


def check_cpu_utilisation():
#Returns average cpu util of a 5 minute interval

    instance_ids = []

    with open('instance_details.json','r') as f:
        data = json.load(f)
        for i in range(0,len(data['instance_details'])):
            id = data['instance_details'][i]['instance_id'][0]
            #print(id)
            instance_ids.append(id)
    #print(instance_ids)
    details_pod = {"instance_id": [],"cpu_usage" : []}
    print(instance_ids)
    list_detail_pod = []
    if len(instance_ids)>0:
        today = datetime.now() - timedelta(minutes=10)
        today_1 = datetime.now() - timedelta(minutes=15)
        starttime = datetime.strftime(today_1, "%Y-%m-%dT%H:%M:%S")
        endtime = datetime.strftime(today, "%Y-%m-%dT%H:%M:%S")
        period = "60"
        statistics = "Average"


        for i in range(len(instance_ids)):
            details_pod = {"instance_id": [],"cpu_usage" : []}
            instance_id = instance_ids[i]
            #print(instance_id)
            command6 = "aws cloudwatch get-metric-statistics --metric-name CPUUtilization --period {} --namespace AWS/EC2 --statistics {} --dimensions Name=InstanceId,Value={} --start-time {} --end-time {} >cpu_util.json".format(period, statistics, instance_id, starttime, endtime)
            subprocess.run([command6], shell = True)
            #print(command6)
            #time.sleep(3)
            f = open('cpu_util.json','r')
            data = json.load(f)
            details_pod["instance_id"] = instance_id
            details_pod["cpu_usage"] = data["Datapoints"][0]["Average"]
            list_detail_pod.append(details_pod)
            os.remove('cpu_util.json')
        f.close()

        print(list_detail_pod)
    else:
        pass

    return list_detail_pod


def run_load_balance_execute(list_detail_pod, dict_attributes):
    instance_id = ''
    if len(list_detail_pod) == 0:
        instance_id = create_instance(instance_type = dict_attributes[7])
        print(instance_id)
        time.sleep(20)
        flag = execute_commands(instance_id,dict_attributes)
        print(flag)
        time.sleep(10)
        if flag:
            time.sleep(5)
            flag2 = check_docker_running(instance_id)
            print(flag2)
            time.sleep(10)
            if flag2 == False:
                flag_terminate = terminate_instance(instance_id)
    else:
        min_usage = list_detail_pod[0]["cpu_usage"]
        min_instance = list_detail_pod[0]["instance_id"]
        for details_pod in list_detail_pod:
            if details_pod["cpu_usage"] < min_usage:
                min_usage = details_pod["cpu_usage"]
                min_instance = details_pod["instance_id"]

        if min_usage > threshold_cpu_usage:
            instance_id = create_instance(instance_type = dict_attributes[7])
            time.sleep(20)
            flag = execute_commands(instance_id, dict_attributes)
            if flag:
                time.sleep(5)
                flag2 = check_docker_running(instance_id)
                if flag2 == False:
                    flag_terminate = terminate_instance(instance_id)
        else:
            flag = execute_commands(min_instance, dict_attributes)

def main():
    dict_attributes = []

    for arg in sys.argv:
        dict_attributes.append(arg)
    #dict_attributes will hold all the attributes necessary to run the flow
    print(dict_attributes)
    list_detail_pod = check_cpu_utilisation()
    run_load_balance_execute(list_detail_pod, dict_attributes)

    pass


if __name__ == '__main__':
    main()
    pass
