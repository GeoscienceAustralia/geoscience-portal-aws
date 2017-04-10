resource "aws_launch_configuration" "lc" {
  name = "${var.stack_name}Dev-WebServerLaunchConfig"
  
  image_id = "${data.aws_ami.image.id}"
  instance_type = "t2.medium"
  key_name = "lazar@work"
  security_groups = ["${var.webserver_sg_id}"]
  
  enable_monitoring = true
  ebs_optimized = false 
}

data "aws_ami" "image" {
  most_recent = true
  owners = ["self"]
  name_regex = "GeosciencePortal"
}
