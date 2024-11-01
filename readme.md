0) Introduction

Ce site est avant tout un projet de mise en pratique et d'apprentissage d'outils informatiques divers. Ce faisant, je serai ravi d'avoir l'avis d'utilisateurs/programmeurs sur mon code, notamment en me conseillant pour l'améliorer.

La première partie donne des informations générales sur l'histoire du projet, les technologies utilisées ainsi que des pistes d'amélioration. La seconde partie entre plus en détail sur la manière dont le site fonctionne et donne des informations nécessaires pour son utilisation.

Technologies utilisées :

    SQL : SQLite, PostgreSQL, SQLAlchemy
    Python : Flask, environnement virtuel
    Automatisation : Planificateur Windows, WSL2 + Apache Airflow (découverte)
    Gestion des versions : Git et GitHub

Ce site est sous licence libre (MIT).

I) Informations générales sur le projet

Vu la nature du projet, il ne faut pas s'étonner si les différentes technologies déployées sur ce site sont redondantes. Par exemple, puisque je voulais apprendre à utiliser différentes technologies pour gérer le SQL, j'ai à la fois utilisé SQLite, notamment pour les données internes du site, et PostgreSQL pour le Pipeline ETL. De même, je peux utiliser sqlite3 et SQLAlchemy. Par ailleurs, j'ai largement utilisé ChatGPT dans l'ensemble du projet.

Pour ce qui est des travaux réalisés jusqu'à présent, ceux-ci ont été :

    Création du site et de sa structure avec SQLite et Flask
    Création d'un système d'authentification (login et rôles)
    Création d'un pipeline ETL pour récupérer des données via l'API d'Ebird en utilisant SQLAlchemy et PostgreSQL
    Utilisation de l'IA de CortexText via son API pour générer du texte

!!! Comme c'est mon premier projet et que certaines technologies sont redondantes, il y a un risque important de bugs.

Pistes d'amélioration envisagées :

A) Général :

    Élimination des coquilles et bugs
    Les tests doivent être mis à jour

B) Authentification / fonctionnalités utilisateurs :

    Utilisateurs envoient des messages ou demandes à l’admin. Mise en place d’un historique de messages.
    Dashboard : infos sur qui tu es, connexion, etc.
    Section commentaire sous une page oiseau
    Ajout d’infos sur les oiseaux : nom latin, espèce en voie de disparition ou non, lieu d’habitation.
    Section géographique dans la liste.

C) Projet data et contenu du site :

    Ajout d'autres sites que Ebird pour trouver des données.
    Pour les images, créer une galerie type tableau.
    Pour les audios, faire une liste.
    Pour les vidéos, créer une galerie déroulante verticalement.
    Faire une carte automatisée des recensements d’oiseaux.

II) Informations techniques sur le projet

Code admin : login : "kiwi" ; mdp : "kiwi" ; celui-ci est imposé dans le code.

Pour un visiteur : Il y a une page d'accueil, une page listant les fiches d'oiseaux disponibles, les oiseaux recensés au Nigeria, les fiches en question et la possibilité de s'inscrire ou de se connecter.

Pour un utilisateur : Il y a, en plus des pages visiteurs, la possibilité de proposer un oiseau ainsi qu'un mode édition qui permet de proposer des ajouts sur les fiches des oiseaux.

Pour un admin : Il y a, en plus des pages utilisateurs, la capacité à accepter ou non les propositions des utilisateurs, ainsi que la capacité à supprimer des pages oiseaux ou de les cacher.

Dans une fiche d'un oiseau, il y a une description, des images, des sons et des vidéos.

Pour la technologie SQLite, je gère la connexion via une fonction get_db_connexion() car celle-ci permet de gérer les tests ainsi que la connexion réelle. Pour les tests, je n'ai pas réussi à bien mocker l'ensemble, donc j'ai créé une BDD tests oiseaux_test.db dédiée à cela (mais attention, c'est juste pour SQLite). Dans le dossier tests/, le fichier client.py constitue la base commune à tous les tests.

Pour l'automatisation de mon pipeline_ETL, j'ai d'abord essayé d'utiliser Apache Airflow via WSL2 (voir dossier WSL-airflow_project, qui ne sert donc pas). J'ai bien réussi l'installation, mais j'ai vite compris que j'irais beaucoup plus vite avec une technologie plus simple comme le planificateur Windows (tache.bat).

Pour les templates, j'ai une base base.html que je complète, de même pour le CSS avec styles.css.

Pour les fichiers audios, vidéos et images, ceux-ci sont stockés dans static/uploads/.

Enfin, vous avez le détail de mes aventures en retraçant les commits sur GitHub.

Bonne journée,

Alexandre Partouche