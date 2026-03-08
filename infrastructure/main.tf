provider "aws" {
  region = "ap-southeast-2"
}
resource "aws_security_group" "rag_bouncer" {
  name        = "rag_web_traffic"
  description = "Allow HTTP and SSH traffic"

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # outgoing traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_instance" "rag_production" {
  ami           = "ami-0ba8d27d35e9915fb"
  instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.rag_bouncer.id]

  tags = {
    Name = "RAG-Production-Server"
  }
  user_data_replace_on_change = true
  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              curl -fsSL https://get.docker.com -o get-docker.sh
              sh get-docker.sh
              sudo usermod -aG docker $USER
              systemctl start docker
              systemctl enable docker
              EOF

}