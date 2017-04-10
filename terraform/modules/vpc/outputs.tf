output "jumpbox_ip" {
  value = "${aws_eip.jump.public_ip}"
}

output "public_subnet_ids" {
  value = ["${aws_subnet.public.*.id}"]
}

output "private_subnet_ids" {
  value = ["${aws_subnet.private.*.id}"]
}

output "webserver_sg_id" {
  value = "${aws_security_group.webserver_sg.id}"
}

output "elb_sg_id" {
  value = "${aws_security_group.elb_http_sg.id}"
}

output "jumpbox_sg_id" {
  value = "${aws_security_group.jumpbox_sg.id}"
}
