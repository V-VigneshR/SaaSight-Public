# SaaSight

**SaaSight** is a cloud-native SaaS product feedback and moderation platform. Inspired by real-world tools like G2, Trustpilot, and Capterra, SaaSight lets users review SaaS tools and product managers monitor, moderate, and manage public sentiment — all with production-grade DevOps workflows.

Deployed via a fully automated **CI/CD pipeline on AWS**, this app is built to simulate scalable, secure, real-time software platforms with role-based functionality.

---

##  Features

###  Users (General Public)
- Register & log in to explore SaaS tools listed on the platform.
- View detailed product pages with existing reviews and ratings.
- Submit reviews for any tool (1–5 star system).
- Flag inappropriate or suspicious reviews.
- View their own submitted reviews in a dashboard.

###  Managers (Product Owners/Moderators)
- Login with elevated access.
- Add new SaaS products to the catalog.
- Monitor user reviews and respond to feedback.
- Receive alerts for flagged/inappropriate reviews in a dedicated **Notifications** tab.
- Remove problematic reviews based on moderation criteria.

---

##  Use Case

SaaSight is ideal for:
- **SaaS founders** who want a lightweight feedback & moderation system.
- **Product managers** managing reputation & review hygiene.
- **Developers & students** showcasing CI/CD pipelines, role-based access control, and cloud deployment.
- **DevOps portfolios** that need real-world workflow simulation.

This project simulates a micro version of enterprise-grade feedback platforms and adds DevOps deployment with **scalable architecture and review moderation**.

---

##  Tech Stack

- **Backend**: Python, Flask, SQLAlchemy ORM
- **Frontend**: HTML5, Bootstrap 5, Jinja2 templating
- **Database**: SQLite (can be swapped with PostgreSQL/MySQL)
- **Authentication**: Flask-Login
- **Deployment**: Gunicorn + Flask app deployed on **Render** (also deployable to EC2)
- **Other Tools**: WTForms, Flask-Flash

---

##  CI/CD Pipeline (AWS)

> SaaSight is deployed through a fully automated **CI/CD pipeline** using AWS services.

###  Pipeline Details:
- **Source Control**: GitHub repo as trigger source
- **CI**: AWS CodeBuild for building and running Docker containers
- **Artifact Management**: Optional S3 bucket for storing built artifacts
- **CD**: AWS CodeDeploy to automatically deploy the Flask app on EC2 with Docker
- **Orchestration**: CloudFormation for infra provisioning

###  Upcoming (Planned Integration):
- **Notification System**: SNS alerts for build and deployment success/failure
- **Rollback Support**: Blue/Green deployment strategy via CodeDeploy appspec hooks

---


