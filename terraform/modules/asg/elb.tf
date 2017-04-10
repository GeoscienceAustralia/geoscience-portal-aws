resource "aws_elb" "loadbalancer" {
  name = "${var.stack_name}Dev-LoadBalancer"
  subnets = ["${var.public_subnet_ids}"]
  security_groups = [
    "${var.elb_sg_id}"
  ]
  cross_zone_load_balancing = false
  idle_timeout = 60
  connection_draining = false
  connection_draining_timeout = 300
  internal = false
  
  listener  {
    instance_port = 8080
    instance_protocol = "http"
    lb_port = 80
    lb_protocol = "http"
  }
  
  health_check {
    healthy_threshold = 2
    unhealthy_threshold = 10
    interval = 300
    target = "HTTP:8080/gmap.html"
    timeout = 30 
  }
  
  tags {
    Name       = "${var.stack_name}_elb"
    owner      = "${var.owner}"
    stack_name = "${var.stack_name}"
    created_by = "terraform"
  }

}