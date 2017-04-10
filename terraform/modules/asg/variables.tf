

variable "private_subnet_ids" {
  type = "list"
}

variable "public_subnet_ids" {
  type = "list"
}

variable "elb_sg_id" {}

variable "webserver_sg_id" {}

variable "jumpbox_sg_id" {}

variable "stack_name" {}

variable "owner" {}

variable "environment" {}