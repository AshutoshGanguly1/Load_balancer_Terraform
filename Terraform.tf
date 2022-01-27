provider "aws" {
    region = "us-east-2"
    access_key = var.access_key[0]
    secret_key = var.access_key[1]
}

variable "access_key" {
  description = "For keeping AWS access keys private"
}

resource "aws_key_pair" "deployer" {
  key_name   = "terraform_keypair"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCi9gxLu9Ph9Nmxyl6lEMWK+N1tIoeUCfvDMp+MB51QXzQPQLDou2AxAXA404HKXsUW0qsfqVjpPOb8HBfXZniKSOwCi/7+3vYBY9yZBRWXtnUo+ENZc4tXTN1oCvS5aE8h2r7og6/2FMeVjQHV3zaYtEh46caXgTDOdlEIEIAkRNDv+Io/2eLz5VNDebornPzejJ9EiRk52kxPq1b8V2d9koJT1vC9kAxiZw9pw2JdGYz8sOt0hwQ7q7iFip2Y0yCXBXxMutR1EumN9got05cDt+AXx3KCo6E08S6DPhtBcFJ9x2j/+ZYitFyQ7lAhO7wOxseC4MrveJ7OY2pPGYdD newkey1"
}

resource "aws_security_group" "terraformsg"{
name = "tf"
vpc_id = "vpc-a1bbb0c9"

ingress{
 from_port = 22
 to_port = 22
 protocol = "tcp"
 cidr_blocks = ["0.0.0.0/0"]
}

egress{
 from_port = 0
 to_port = 0
 protocol = "-1"
 cidr_blocks = ["0.0.0.0/0"]
}

}
