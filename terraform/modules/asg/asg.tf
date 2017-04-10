resource "aws_autoscaling_group" "webserver" {
    desired_capacity = 1
    health_check_grace_period = 300
    health_check_type = "ELB"
    launch_configuration = "${aws_launch_configuration.lc.name}"
    max_size = 1
    min_size = 1
    name = "${var.stack_name}Dev-asg"
    vpc_zone_identifier = ["${var.private_subnet_ids}"]
    load_balancers = ["${aws_elb.loadbalancer.name}"]

    tag {
      key = "Name"
      value = "${var.stack_name}Dev-asg"
      propagate_at_launch = true
    }
    
    tag {
      key                 = "owner"
      value               = "${var.owner}"
      propagate_at_launch = true
    }

    tag {
      key                 = "environment"
      value               = "${var.environment}"
      propagate_at_launch = true
    }

    tag {
      key                 = "stack_name"
      value               = "${var.stack_name}"
      propagate_at_launch = true
    }

    tag {
      key                 = "created_by"
      value               = "terraform"
      propagate_at_launch = true
    }
}