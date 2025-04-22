# `cyber-students`

This repository provides some sample code for the Shared Project for
Modern Cryptography and Security Management & Compliance.  The project
requires git, Python 3, and MongoDB.  The following sections briefly
explain how to setup the project on your local machine.

## Get the Sample Code

Create a [GitHub](https://github.com) account.  Download and install
[git](https://git-scm.com).  We will use `git` to manage our source
code.

Verify that `git` is installed correctly:

```sh
git --version
```

[Fork this
repository](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
and clone your forked repository to your local machine:

```sh
git clone https://github.com/YOUR_GITHUB_USERNAME/cyber-students.git
```

## Setup the Project

Create a Python 3 virtual environment:

```sh
python -m venv project-venv

```

Activate the virtual environment:

```bat
:: ... on Windows:
.\project-venv\Scripts\activate
```

```sh
# ... on macOS/*nix:
source project-venv/bin/activate
```

Install the required packages:

```sh
cd cyber-students
pip install -r requirements.txt
```

Download, install and start [MongoDB Community
Edition](https://www.mongodb.com/docs/manual/installation).  We will
use MongoDB as our database.

Download and install [MongoDB
Shell](https://www.mongodb.com/try/download/shell).  Open a MongoDB
shell:

```sh
mongosh
```

Create two databases with a collection named `users` in each:

```
use cyberStudents;
db.createCollection('users');

use cyberStudentsTest;
db.createCollection('users');
```

The first database will store our 'real' data.  The second database
will be used by our tests.

### Postman
Download and install **the Postman app** https://www.postman.com/downloads/

Download the **Cyber-student.postman_collection** 
 - This collection contains all 5 updated requests - Welcome, Registration, Login, Display User Logout


With the Postman App open, Select **Workspace** >> **Create Workspace** called crypto

Select **Import** >> **Files** >> Select the **Cyber-student.postman_collection** file >> **Import**


### Alternatively, use Curl

Download and install [curl](https://curl.se).  
`curl` is also shipped by Microsoft as part of Windows 10 and 11.  
`curl` is a command-line tool for interacting with web servers (and other protocols).

Verify that `curl` is installed correctly:

```sh
curl --version
```

## Start the Project

The server contains functionality for:

* registering new users (`api/handlers/registration.py`)
* logging in (`api/handlers/login.py`)
* logging out (`api/handlers/logout.py`)
* displaying profile (`api/handlers/user.py`)

To start the server:

```sh
python run_server.py
```

The server is available on port 4000 at
http://localhost:4000/students/api.  However, it is not possible to
use all of the functionality offered by the server directly using a
browser.  
Instead, we will use `curl` or `Postman` to interact with the server.

**Welcome Request in Postman**  
The image below shows the request and the desired returned output 

![image](https://github.com/user-attachments/assets/91b96e55-2d7b-4474-89c4-4fb8488aea91)


### Registration

To register a new user:

```sh
curl -X POST http://localhost:4000/students/api/registration -d "{\"email\": \"foo@bar.com\", \"password\": \"pass\", \"displayName\":\"Foo2Bar\",\"fullName\":\"Student foo1\",\"address\":\"Dublin\",\"phone\":\"0000000000\",\"disabilities\":\"Diabetic\",\"dob\":\"01/01/1981\"}"
```

If the registration is successful, it will confirm the email address
and the display name of the newly registered user:

```
{"email": "foo@bar.com", "displayName": "Foo Bar"}
```

If the registration is unsuccessful, for example, if you try to
register the same user twice, it will return an error message:

```
{"message": "A user with the given email address already exists!"}
```
**Registration request in Postman**  

![image](https://github.com/user-attachments/assets/174f62fa-aada-4892-951b-8e265a61d591)

### Logging In

To login:

```sh
curl -X POST http://localhost:4000/students/api/login -d "{\"email\": \"foo@bar.com\", \"password\": \"pass\"}"
```

If the login is successful, it will return a token and an expiration date
timestamp:

```
{"token": "d4a5d8b20fe143b7b92e4fba92d409be", "expiresIn": 1648559677.0}
```

A token expires and is intended to be short-lived.  A token expires
two hours after login, after a logout, or if there is another login
from the same user, generating a new token.

If the login is unsuccessful, for example, if you provide an incorrect
password, it will return an error message:

```
{"message": "The email address and password are invalid!"}
```
**Login request in Postman**  

![image](https://github.com/user-attachments/assets/857ade9e-7955-43d0-a465-0098b1a27452)
 **"token" value added to "X-TOKEN" variable**
![image](https://github.com/user-attachments/assets/c921c953-6701-4d5c-a5d8-9bf1ef0e5be7)

 - Please note that upon successful login, the token value returned **"token": "6c50e75ce057414ab43b0661be392ba9"** will need to be added to the collections variable **"X-TOKEN"** then hit **Save** <ins>before running the Display User or Logout requests.</ins>
 
### Displaying a Profile

To display a user's profile you need to a token that has not expired.
Then you can use:

```sh
curl -H "X-TOKEN: d4a5d8b20fe143b7b92e4fba92d409be" http://localhost:4000/students/api/user
```

Note that this API call does not require the `-X POST` flag.

If successful, it will return the email address and the display name
for the user:

```
{"email": "foo@bar.com", "displayName": "Foo Bar"}
```

**Display User request in Postman**  

![image](https://github.com/user-attachments/assets/706970d9-f911-4bce-bbc9-f7b7ef582447)


### Logging Out

To logout, you also need a token that has not expired.  Then you can
use:


```sh
curl -X POST -H "X-TOKEN: d4a5d8b20fe143b7b92e4fba92d409be" http://localhost:4000/students/api/logout
```
**Logout request in Postman**  

![image](https://github.com/user-attachments/assets/17c43750-d045-45c8-8b4b-e2fa2cf497a9)


## Test the Project

You can run the automated tests using:

```sh
python run_test.py
```

This command runs a number of automated tests in the `tests` folder.
The tests read and store data in the `cyberStudentsTest` database
only.  They perform tests such as registering new users
(`tests/registration.py`), logging in (`tests/login.py`), and logging
out (`tests/logout.py`).

The project also includes a program called `run_hacker.py`.  You can
run it using:

```sh
python run_hacker.py list
```

It displays all information stored in the MongoDB database.  It
produces output similar to the following:

```
There are 1 registered users:
{'_id': ObjectId('6242d9c34536b3a16b49aa6b'), 'email': 'foo@bar.com', 'password': 'pass', 'displayName': 'Foo Bar'}
```

As you can see, all of the information is stored in the clear; there
is no encryption or password hashing.  If a hacker was to compromise
the database, they could easily run a similar program to retrieve all
of the users' personal information and passwords.

### Secure Code implemented

After updating the code, the following security measures were added:

**registration.py**  
 - AES-CTR encryption: Was applied to the following fields (fullName, address, phone, disabilities and dob), they are now encrypted using the Algorithm: AES-256 in CTR mode with a random Key of 32 bytes (256 bits) and random nonce of 16 bytes (128 bits)
 - Password Hashing: Was also implemented using `bcrypt` with a unique salt `bcrypt.gensalt()` to ensure the password is securely hashed.

**user.py**  
 - Decryption: AES-CTR will be used to match the key/nonce value loaded from the secure `keyfile`.
 - User profile details will be decrypted before being displayed to a logged-in user.
 - Key Management: Reads keys and nonces per field name from the `keyfile`.
 - To avoid crashes, code has been added to safely handle missing or malformed ciphertext
  
**login.py**  
 - Secure Password Verification: Incoming passwords are now hashed using stored salt and `bcrypt.hashpw`. They are then compared to the stored bcrypt hash for authentication.
 - Token Issuance: Upon successful login, the code will generate a secure, random session token (uuid4().hex) with a 2-hour expiry window.

**base.py**
 - Centralised Response Handling: All JSON output is written through `write_json()` to ensure consistent and clean structure.
 - CORS Headers: Ensures secure API access with controlled CORS behaviour.
   
**Tests after Code has been fixed**  

`run_hacker.py list`
![image](https://github.com/user-attachments/assets/584f8203-32dd-452b-b3e6-97061ed491c0)

`run_test.py`
![image](https://github.com/user-attachments/assets/83e1fb22-326a-416e-9469-df9bf20d305e)


