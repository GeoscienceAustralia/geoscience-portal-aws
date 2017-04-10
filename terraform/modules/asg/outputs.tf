output "asg_id" {
  value = "${aws_autoscaling_group.webserver.id}"
}

output "elb_name" {
  value = "${aws_elb.loadbalancer.name}"
}

output "elb_dns_name" {
  # Return the dns_name of whichever elb was created
  value = "${aws_elb.loadbalancer.dns_name}"
}

output "elb_dns_hosted_zone" {
  # Return the zone_id of whichever elb was created
  value = "${aws_elb.loadbalancer.zone_id}"
}

output "webapp_lc_id" {
  value = "${aws_launch_configuration.lc.id}"
}

output "webapp_lc_name" {
  value = "${aws_launch_configuration.lc.name}"
}