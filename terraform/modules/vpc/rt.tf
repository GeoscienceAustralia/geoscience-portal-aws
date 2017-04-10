resource "aws_route_table" "public_rt" {
  vpc_id = "${aws_vpc.vpc.id}"
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.default.id}"
  }
}

resource "aws_route_table" "private_rt" {
  vpc_id = "${aws_vpc.vpc.id}"
  route {
    cidr_block = "0.0.0.0/0"
    instance_id = "${aws_instance.jumpbox.id}"
  }
}

resource "aws_route_table_association" "public_rta" {
  route_table_id = "${aws_route_table.public_rt.id}"
  subnet_id = "${aws_subnet.public.0.id}"
  
}

resource "aws_route_table_association" "private_rta" {
  route_table_id = "${aws_route_table.private_rt.id}"
  subnet_id = "${aws_subnet.private.0.id}"
  
}