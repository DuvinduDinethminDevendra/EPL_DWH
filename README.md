
# EPL Data Warehouse Project

This project implements an ETL (Extract, Transform, Load) pipeline to build a Star Schema Data Warehouse for English Premier League (EPL) match and player statistics. The database is hosted in a dedicated MySQL Docker container to ensure a consistent environment across development machines.

## Prerequisites

To run this project, you must have the following software installed on your system:

  * **Docker Desktop:** (Includes Docker Engine and Docker Compose)
  * **Python 3.9+**
  * **Git**

## Setup Guide

Follow these steps to get the environment running on your local machine.

### 1\. Clone the Repository

```bash
git clone https://github.com/DuvinduDinethminDevendra/EPL_DWH
cd EPL_DWH
```

### 2\. Configure the Database (Docker)

This project uses Docker Compose to manage the MySQL database container.

**Create the `docker-compose.yml` file** (if you don't have one yet) and define your MySQL service.


```yaml
version: "3.8" # OK, but can be removed for modern Compose V2
services:
  db:
    image: mysql:8.0
    container_name: epl_mysql
    restart: unless-stopped
    environment:
     
      MYSQL_ROOT_PASSWORD: 1234 #password
      MYSQL_DATABASE: epl_dw
    ports:
      
      - "3307:3306" 
    volumes:
      - ./mysql_data:/var/lib/mysql
      - ./src/sql:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  adminer:
    image: adminer
    restart: unless-stopped
    ports:
      - "8080:8080"
    
    depends_on:
      - db
```

**Start the Container:**

Run the following command in the project root directory. This will download the MySQL image, create the `epl_dw` database, and execute the `create_schema.sql` script to build your tables.

```bash
docker-compose up -d
```
OR IF NEED TO CREATE A LOCAL INSTANCE AS WELL
```bash
mysql -u root -p1234 < "src\sql\create_schema.sql"
```

### 3\. Setup Python Environment

This project uses a virtual environment (`.venv`) for dependency management.

**A. Create and Activate the Virtual Environment**

On Windows (PowerShell):

```powershell
# Create the environment
py -m venv .venv

# Activate the environment (Required for every new terminal session)
. .venv/Scripts/Activate.ps1
```

*(Your prompt should now start with `(.venv)`)*

**B. Install Python Dependencies**

Ensure you have a `requirements.txt` file listing packages like `sqlalchemy` and `mysql-connector-python`.

```bash
# Example contents of requirements.txt:
# sqlalchemy
# mysql-connector-python
# pandas

pip install -r requirements.txt
```

### 4\. Run the ETL Pipeline

Once the database container is running and the Python environment is active, you can run your main ETL script.

```bash
python src/etl/main.py 
or
python -m src.etl.main
 ```

## Database Connection Details

These details are used by the Python application to connect to the Docker container.

| Setting | Environment Variable | Default Value | Docker Service Name |
| :--- | :--- | :--- | :--- |
| **Host** | `MYSQL_HOST` | `localhost` | `epl_mysql` |
| **Port** | `MYSQL_PORT` | `3307` | N/A (Host Port) |
| **User** | `MYSQL_USER` | `root` | `root` |
| **Password** | `MYSQL_PASSWORD` | `1234` | `1234` |
| **Database** | `MYSQL_DB` | `epl_dw` | `epl_dw` |

## Viewing the Database

You can connect to the running `epl_mysql` container using any standard database client (e.g., DBeaver, MySQL Workbench, TablePlus) with the connection details provided above.

**Host:** `localhost`
**Port:** `3307`
**User:** `root`
**Password:** `1234`

## Cleanup

To stop and remove the Docker container and its data (if you didn't use a volume, otherwise it just stops the service):

```bash
docker-compose down
```

To deactivate the virtual environment:

```bash
deactivate
```
