The process of completing homework:
1. Created auth form and working process with users and sessions via flask_login. Class UserLogin is used there for fast getting user info in different functions
2. All pages are closed only for authenticated users, except some pages like "Register", "Login"
3. Redirect after successfull login to profile page
4. User name, password and some additional information for next steps are stored in Mongo
5. On profile page under main avatar user can change avatar, password, summary information in profile and make a logout.
6. Password is stored in Mongo as a hash using sha256 algorithm
7. User can update profile picture via "Change avatar" button. All pictures are stored in avatars/ folder and has a filename equals to username. If user has not uploaded avatar yet, there will be a default one.
8. User can update some profile information via "Update profile" button. In this case, for example, if user has not updatet Summary Info yet, there will be a default summary string, as for a picture. This information stored in Mongo aswell.
