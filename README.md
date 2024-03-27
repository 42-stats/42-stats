# <p align="center">42 Stats </p>
  
The 42 Stats CLI is a command-line tool designed for 42 students. It allows users to easily access and analyze various statistics related to their curriculum.
## 🧐 Features    
- **Average Score as an evaluator:** Get the average score you've given as an evaluator
- **Odds of failing your next project:** Estimate the likelihood of not passing your next project

## 🛠️ Installation
To use the 42 Stats CLI, you will need Python installed on your machine. Follow these steps to get started:

1.  **Clone the repository:**
```sh
git clone https://github.com/winstonallo/42-stats.git
cd 42-stats
```
2. **Install dependencies:**
```sh
pip install -r requirements.txt
```
## 📡 API Configuration
The 42 Stats CLI interacts with the 42 API to fetch student and curriculum data. To access the 42 API, you'll need to get your own API key.
### Obtaining an API Key
1. On the 42 intra, go to settings -> API (https://profile.intra.42.fr/oauth/applications)
2. Create an application to receive your API credentials
### Configuring the API Key
Once you have your key, you will need to set it in your environment variables to keep it secure and separate from the application code.
*  Set up your **'.env'** File

In the root directory, create a file named **'.env'**. Your 42 API key consists of 2 values that will both be needed for authentification:
1. **UID**
2. **SECRET**

Add them to your **'.env'** file:
```sh
API_UID="<your UID>"
API_SECRET="<your secret>"
```
## 🧑🏻‍💻 Usage
To launch the CLI, run
```
python3 main.py
```
Follow the on-screen prompts to navigate through the different options.

## 🍰 Contributing    
Contributions are welcome! If you have a suggestion for improving this tool or have found a bug, please open an issue on the repository.

Additionally, if you would like to contribute code, please fork the repo and submit a pull request.

1.    **Fork the project**
2.    **Create your feature branch (`git checkout -b feature/amazing-feature`)**
3.    **Commit and push your changes**
4.    **Open a pull request**
                
## 🙇 Authors
- [@ifaoji](https://github.com/ifaoji)
- [@winstonallo](https://github.com/winstonallo)
