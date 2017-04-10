resource "aws_vpc" "vpc" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = false
  enable_dns_support = true
  instance_tenancy = "default"
}

resource "aws_internet_gateway" "default" {
  vpc_id = "${aws_vpc.vpc.id}"
}

resource "aws_eip" "nat" {
  vpc = true
}