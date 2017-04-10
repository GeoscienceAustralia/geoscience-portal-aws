resource "aws_instance" "jumpbox" {
  ami = "ami-48d38c2b"
  availability_zone = "ap-southeast-2a"
  ebs_optimized = false
  instance_type = "t2.micro"
  monitoring = false
  key_name = "lazar@work"
  
  subnet_id = "${aws_subnet.public.0.id}"
  
  vpc_security_group_ids      = ["${aws_security_group.jumpbox_sg.id}"]
  associate_public_ip_address = true
  private_ip = "10.0.0.60"
  source_dest_check = true
  
  root_block_device {
    volume_type = "gp2"
    volume_size = 8
    delete_on_termination = true
  } 
  
  tags {
    Name       = "${var.stack_name}Dev-jumpbox"
    owner      = "${var.owner}"
    stack_name = "${var.stack_name}"
    created_by = "terraform"
  }
}

resource "aws_eip" "jump" {
  instance = "${aws_instance.jumpbox.id}"
  vpc = true
}