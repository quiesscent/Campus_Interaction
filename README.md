# Kenyan Universities Interaction and Trending News Website

## Project Overview
This project is a web-based platform designed to engage university students, faculty, and the wider academic community in Kenya. The platform offers interactive features such as news updates, discussion forums, event calendars, resource sharing, and live messaging. The goal is to create an engaging and informative space for students to connect, share academic resources, and stay updated on trending topics across Kenyan universities.

## Features
1. **Live Charts & Messaging**  
   - Frontend: Jean  
   - Backend: Fidel  

2. **Feeds, Trending Topics & Hashtags**  
   - Frontend: Fabian  
   - Backend: Fidel  

3. **Polls**  
   - Frontend: Debby  
   - Backend: Victor  

4. **Event Calendar**  
   - Frontend: Saints  
   - Backend: Incognito  

5. **Discussion Forums & Student Communities**  
   - Frontend: Victor  
   - Backend: Fidel  

6. **News and Updates**  
   - Both Frontend and Backend: Mato  

7. **Maps**  
   - Both Frontend and Backend: Peter  

8. **Resource Sharing & Academic Tools**  
   - Both Frontend and Backend: Samtech  

9. **Marketplace**  
   - Both Frontend and Backend: Victor  

10. **Student Profiles & Networking**  
    - Both Frontend and Backend: Fidel

## Technology Stack
- **Frontend:** HTML, CSS, JavaScript (React, Vue, or Angular based on the developer's choice)
- **Backend:** Django
- **Database:** sqlite
- **API Services:** RESTful APIs for communication between frontend and backend components

## Project Structure
### Frontend
- **Jean:** Live Charts & Messaging  
- **Fabian:** Feeds, Trending Topics & Hashtags  
- **Debby:** Polls  
- **Saints:** Event Calendar  
- **Victor:** Discussion Forums & Student Communities

### Backend
- **Fidel:** Live Charts & Messaging, Feeds, Discussion Forums
- **Victor:** Polls, Marketplace  
- **Incognito:** Event Calendar  
- **Mato:** News and Updates  
- **Peter:** Maps  
- **Samtech:** Resource Sharing & Academic Tools

### Both Frontend & Backend
- **Mato:** News and Updates  
- **Peter:** Maps  
- **Samtech:** Resource Sharing & Academic Tools  
- **Victor:** Marketplace
- **Fidel:** Student Profiles & Networking  

# How to setup the project for dev

## 1. Clone the repo

```bash
git clone https://github.com/KenyanAudo03/Campus_Interaction.git
cd Campus_Interaction
```

## 2.  Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Initialize the database and other dirs
```bash
python manage.py makemigrations
python manage.py makemigrations profiles
python manage.py migrate
mkdir  static staticfiles
```

## 4.  Run the project
```bash
python manage.py runserver
```

## 5. Create a new app
```bash
django-admin startapp your_app
```

# How to Git Commit and Push

Follow these steps to commit your changes and push them to the remote repository:

## 1. Clone the Repository
If you haven't already cloned the repository, you can do so using the following command:

```bash
git clone https://github.com/KenyanAudo03/Campus_Interaction.git
cd Campus_Interaction

git checkout -b your-feature-branch
git add .
git commit -m "Add feature description or fix details"
git push origin your-feature-branch
```

