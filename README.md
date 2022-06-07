# ao_laerer_projeto
 
Å lære is a language Exchange web application on which an user can share short classes explaining something that they know. The project is coded using Django framework based on Python.

> :construction: Description under construction :construction:


##### Table of Contents  
[Instructions](#instructions)

[Programming tools](#programming-tools)

[Functionalities](#functionalities)  



## Functionalities

- ` 1 Changing theme - Light and dark theme `:
The application has the funcionality to change its theme. There are two theme: dark and light. The base color, which is some kind of purple, is mantained through both themes.

<p align="center">
<img width="400" src="https://user-images.githubusercontent.com/90400199/172223246-e422dba8-10ff-41e9-a9fd-4328fc176552.gif">
</p>

- ` 2 User functionality - Creating a new user `: 
The functionality contains a simple form on which a person can put their informations, such as name, email, in order to create a new user to be able to access all language Exchange functionalities.
<p align="center">
<img width="400" src="https://user-images.githubusercontent.com/90400199/172085473-506eebff-bb10-4a06-ae9c-112b32749a5b.gif">
</p>


- ` 2.a User functionality - Updating a user`:
The application provides a view with which a user can update their informations. In this view the user can change their profile image, their password and their name and surname.
<p align="center">
<img width="400" src="https://user-images.githubusercontent.com/90400199/172085604-80ba28ae-585d-421e-b555-2c6eadca0d7a.gif">
</p>


- ` 3 Learning and teaching functionality - Creating a new class`:
All registered users have the permission to create normal class, the only requirement is the conclusion of licenced classes before posting new contents (the manner to conclude will be commented below, on section 3.a). For instance, always that a new language is added to the application, it will be added with five modules (which is based on Common European Framework of Reference for Languages – CEFR). So, after concluding A1 module a user can post a A1 class and access A2 module.
<p align="center">
<img width="550" height="auto" src="https://user-images.githubusercontent.com/90400199/172085902-f715585c-ea9f-432f-a00a-3872eee7522b.gif">
</p>


- ` 3.a Learning and teaching functionality - Accessing a class `:
The languages are sorted on the languages menu. After choosing which idiom to study, a user is redirected to idiom page, which is separated in three sections: Class, Forum and Dictionary. The first view is the classes. This view displays the normal classes and the licenced modules. The user can enter to a licenced class through the modules. To conclude a class, the user can watch the class vídeo and, after it, do the activite linked to the class. The way to finish a class is to have 70% or more of the questions marked as correct.
<p align="center">
<img width="550" src="https://user-images.githubusercontent.com/90400199/172086382-ae6d325e-cc59-4722-b131-ffb95ea8f71a.gif">
</p>



- ` 4 Dictionary funcionality - Adding a new word `:
Users can add a new word to the app. The view of it is a form on which the word creator put the word on the first field, which idiom it belongs to and another informations. In case the word added is not new on the DataBase, the word will not be added, but the context put by the user will be added to the context's word.
<p align="center">
<img width="500" src="https://user-images.githubusercontent.com/90400199/172088077-d30fefc9-51e8-4dcf-9f27-1d8ae0941acb.gif">
</p>

- `4.a Dictionary funcionality - Accessing a dictionary `:
Accessing a dictionary is very simples, it will be shown at language page, it means the user has to access which idiom they would like to access a dictionary. The dicitonary is formed by a search bar, in which the user can put some word, and a container, in that recent words are shown.
If the user enter a word which is not recognised by the database, they will be redirected to a similar pages, and can find a similar word.
Below there is a example of it. The word's page displays all word's informations.

<p align="center">
<img width="550" src="https://user-images.githubusercontent.com/90400199/172088095-7a20ad2b-d7a8-4b44-950d-1bed10da9243.gif">
</p>


<p align="center">
<img width="400" src="https://user-images.githubusercontent.com/90400199/172226079-cddf1783-713b-4c85-a185-3265a1802536.gif">
</p>


## Instructions

First step is activate the virtual enviroment, after it, the user can copy and paste these commands:

`
pip install django
`

`
pip install bycript
`

`
pip install mysql-client
`

`
pip install Pillow
`

It will provide the virtual environment with the knowledge of applying properly frameworks utilised.

## Programming tools

The project has used some programmings tools to reach the result. The principle programming language utilised is Python 3.10.3. Since the app is a web application, this case claims a Framework with which the developer can expedite its development, so it has been used Django 4.0.4 framework.
Another tools are HTML 5, CSS 3 and JavaScript (JQuery). For to save datas, the app has utilised MySql Workbech DataBase.
