#only run to reset everthing
#creates a blank tf state file, a blank intance_details file

with open('instance_details.json', 'w') as f:
    file = ' { \n    "instance_details": [    ] \n  } '
    f.write(file)
    f.close()

with open('terraform.tf','w') as f:
    file = 'provider "aws" { \n  region = "us-east-2" \n access_key = var.access_key[0] \n secret_key = var.access_key[1] \n } \n variable "access_key" { \n description = "For keeping AWS access keys private" \n } \n resource "aws_key_pair" "deployer" {\n key_name   = "terraform_keypair"\n public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCi9gxLu9Ph9Nmxyl6lEMWK+N1tIoeUCfvDMp+MB51QXzQPQLDou2AxAXA404HKXsUW0qsfqVjpPOb8HBfXZniKSOwCi/7+3vYBY9yZBRWXtnUo+ENZc4tXTN1oCvS5aE8h2r7og6/2FMeVjQHV3zaYtEh46caXgTDOdlEIEIAkRNDv+Io/2eLz5VNDebornPzejJ9EiRk52kxPq1b8V2d9koJT1vC9kAxiZw9pw2JdGYz8sOt0hwQ7q7iFip2Y0yCXBXxMutR1EumN9got05cDt+AXx3KCo6E08S6DPhtBcFJ9x2j/+ZYitFyQ7lAhO7wOxseC4MrveJ7OY2pPGYdD newkey1"\n } \n \n resource "aws_security_group" "terraformsg"{ \n name = "tf" \n vpc_id = "vpc-a1bbb0c9" \n ingress{\n from_port = 22 \n to_port = 22 \n protocol = "tcp" \n cidr_blocks = ["0.0.0.0/0"] \n } \n egress{ \n from_port = 0 \n to_port = 0 \n protocol = "-1" \n cidr_blocks = ["0.0.0.0/0"] \n } \n }'
    f.write(file)
    f.close()
