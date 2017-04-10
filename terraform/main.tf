provider "aws" {
  profile = "geoscience-portal"
  region = "${var.region}"
}

module "vpc" {
  source = "modules/vpc"
  
  stack_name = "${var.stack_name}"
  owner = "${var.owner}"
  environment = "${var.environment}"
}

module "asg" {
  source = "modules/asg"
  elb_sg_id = "${module.vpc.elb_sg_id}"
  webserver_sg_id = "${module.vpc.webserver_sg_id}"
  jumpbox_sg_id = "${module.vpc.jumpbox_sg_id}"
  
  public_subnet_ids = "${module.vpc.public_subnet_ids}"
  private_subnet_ids = "${module.vpc.private_subnet_ids}"
  
  stack_name = "${var.stack_name}"
  owner = "${var.owner}"
  environment = "${var.environment}"
}

