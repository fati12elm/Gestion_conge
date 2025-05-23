# Application de Gestion des Congés

Une application web moderne pour la gestion des congés d'entreprise, développée avec Django.

## Fonctionnalités

- Gestion des utilisateurs avec différents rôles (Employé, Manager, RH, Admin)
- Demande de congés avec pièces jointes
- Validation des demandes par les managers et RH
- Suivi des soldes de congés
- Notifications en temps réel
- Export de rapports
- Interface responsive et moderne

## Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)
- Virtualenv (recommandé)

## Installation

1. Cloner le dépôt :
```bash
git clone https://github.com/fati12elm/Gestion_conge.git
cd gestion-conges
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer la base de données :
```bash
python manage.py migrate
```

5. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur de développement :
```bash
python manage.py runserver
```

L'application sera accessible à l'adresse : http://127.0.0.1:8000/

## Structure du Projet

```
leave_management/
├── accounts/            # Application de gestion des utilisateurs
├── leaves/             # Application de gestion des congés
├── templates/          # Templates HTML
├── static/            # Fichiers statiques (CSS, JS, images)
├── media/             # Fichiers uploadés
└── leave_management/  # Configuration du projet
```

## Utilisation

1. Se connecter avec les identifiants créés
2. Les employés peuvent :
   - Consulter leurs soldes de congés
   - Soumettre des demandes de congés
   - Suivre l'état de leurs demandes
   - Ajouter des pièces justificatives

3. Les managers peuvent :
   - Valider/refuser les demandes de leur équipe
   - Consulter les soldes de leur équipe
   - Générer des rapports

4. Les RH peuvent :
   - Gérer tous les congés
   - Gérer les soldes
   - Générer des rapports globaux

## Sécurité

- Authentification requise pour toutes les actions
- Gestion des permissions par rôle
- Protection CSRF
- Validation des données
- Hachage des mots de passe

## Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

- Samah El Azzab
- Fatima Zahra El Mouhandiz
- Naimi Mohamed

Projet encadré par : Yves Frédéric Ebobisse Djene 