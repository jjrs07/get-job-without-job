
# 🛠️ Deploying Flask + RDS MySQL on Amazon EC2 using S3 User Data

This guide walks you through setting up a Flask app on an Amazon EC2 instance (Amazon Linux 2023) that connects to an Amazon RDS MySQL database. The app is bootstrapped automatically using **EC2 user data** and pulls your code from an **Amazon S3 bucket**.

---

## ✅ Architecture Overview

```
[ HTML Form (S3) ] ---> [ Flask App on EC2 ] ---> [ RDS MySQL ]
```

---

## 📦 What You'll Need

- An **Amazon EC2** instance running Amazon Linux 2023
- An **Amazon RDS MySQL** instance
- An **S3 bucket** containing `app.py` and optionally your `index.html`
- An **IAM role** with S3 read access attached to your EC2 instance

---

## 📝 Step 1: Upload `app.py` to S3

1. On your AWS Console, open the cloudshell 
2. Upload your 'app.py' in the cloudshell
3. Create a bucket or choose an existing one.

```bash
aws s3 mb s3://your-s3-bucket-name
```
4. Upload your `app.py`

```bash
aws s3 cp app.py s3://your-s3-bucket-name/your-folder-path/app.py
```

---

## 🔒 Step 2: Configure EC2 IAM Role for S3 Access

Attach this policy to the IAM role:

```json
{
  "Effect": "Allow",
  "Action": "s3:GetObject",
  "Resource": "arn:aws:s3:::your-s3-bucket-name/your-folder-path/app.py"
}
```

Attach the role to your EC2 during launch.

---

## 🚀 Step 3: Launch EC2 with User Data

Paste the script below into the **User data** section during EC2 launch (under Advanced Details):

```bash
#!/bin/bash
dnf update -y
dnf install -y python3 python3-pip awscli

pip3 install --upgrade pip
pip3 install Flask mysql-connector-python flask-cors

mkdir -p /home/ec2-user/flaskapp
cd /home/ec2-user/flaskapp

aws s3 cp s3://your-s3-bucket-name/your-folder-path/app.py .

nohup python3 app.py > output.log 2>&1 &
```

✔️ Make sure to replace `your-s3-bucket-name` and `your-folder-path`.

---

## 🔧 Step 4: Security Groups

### EC2 Security Group
- Inbound:
  - TCP 22 (SSH)
  - TCP 5000 (Flask)
  - Optional: TCP 80 (Nginx)

### RDS Security Group
- Inbound:
  - TCP 3306 from EC2 security group

---

## 🗄️ Step 5: Create MySQL Table in RDS

Connect from EC2:

```bash
mysql -h <your-rds-endpoint> -u admin -p
```

Then run:

```sql
CREATE DATABASE cloud_form;
USE cloud_form;

CREATE TABLE personal_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100),
    email VARCHAR(100),
    address TEXT,
    phone VARCHAR(20)
);
```

---

## 🧪 Step 6: Test

- Access the HTML form in browser (host locally or via S3)
- Set `action="http://<your-ec2-public-ip>:5000/submit"` in `index.html`
- Submit form
- Verify data in RDS:

```bash
SELECT * FROM cloud_form.personal_details;
```

---

## 🌐 Bonus: Host HTML Form on S3 as a Static Website

You can host your HTML form (`index.html`) on S3 and connect it to your Flask API running on EC2.

### 🧾 Step 1: Create an S3 Bucket

```bash
aws s3 mb s3://your-html-bucket-name
```

Make sure the name is globally unique.

---

### 📤 Step 2: Upload HTML File

```bash
aws s3 cp index.html s3://your-html-bucket-name/
```

---

### 🌍 Step 3: Enable Static Website Hosting

```bash
aws s3 website s3://your-html-bucket-name/ --index-document index.html
```

---

### 🔒 Step 4: Make the File Public

Create a file called `bucket-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::your-html-bucket-name/*"
  }]
}
```

Apply the policy:

```bash
aws s3api put-bucket-policy --bucket your-html-bucket-name --policy file://bucket-policy.json
```

---

### 🚀 Step 5: Access Your Form

Navigate to:

```
http://your-html-bucket-name.s3-website-<region>.amazonaws.com
```

Then set the form’s `action` to point to your EC2 backend:

```html
<form action="http://<your-ec2-public-ip>:5000/submit" method="post">
```

---

## 🧹 Optional Enhancements

- Use **Gunicorn + Nginx** for production
- Add **SSL (HTTPS)** via Let's Encrypt
- Store credentials in **AWS Secrets Manager**
- Use **environment variables** for config

---

## ✅ Done!

Your Flask app now connects EC2 and RDS using a fully automated S3-based provisioning workflow, with a static website front-end hosted on S3. 🎉
