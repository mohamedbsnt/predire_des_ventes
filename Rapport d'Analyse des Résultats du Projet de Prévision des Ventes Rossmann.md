# Rapport d'Analyse des Résultats du Projet de Prévision des Ventes Rossmann

## 1. Introduction

Ce rapport a pour objectif de détailler et d'expliquer les résultats obtenus dans le cadre du projet de prévision des ventes pour un réseau de magasins, en s'appuyant sur les visualisations générées par l'application Streamlit. Ces visualisations sont essentielles pour comprendre la performance du modèle et son utilité opérationnelle pour la prise de décision.

## 2. Contexte des Visualisations

L'application développée dans le cadre de ce projet intègre un tableau de bord interactif permettant aux utilisateurs d'explorer les prévisions de ventes. Deux types de visualisations principales sont présentées ici : une simulation unitaire pour des scénarios spécifiques et une projection future sur un horizon temporel défini. Ces outils visent à rendre les prévisions accessibles et exploitables par un public non technique.

## 3. Analyse Détaillée des Résultats

### 3.1. Courbe Prévisionnelle des Ventes (Simulation Unitaire)

La première visualisation (Figure 1) illustre l'interface de simulation unitaire de l'application. Elle permet à l'utilisateur de configurer divers paramètres liés à un magasin spécifique et d'observer en temps réel la courbe prévisionnelle des ventes associée. 

![Courbe Prévisionnelle des Ventes (Simulation Unitaire)](https://private-us-east-1.manuscdn.com/sessionFile/zhTMAjfnt5eBFUykE4Y1Kl/sandbox/5UItHLS1xuYSpiakPPRETP-images_1781179313694_na1fn_L2hvbWUvdWJ1bnR1L2ZpZ3VyZV9zaW11bGF0aW9u.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvemhUTUFqZm50NWVCRlV5a0U0WTFLbC9zYW5kYm94LzVVSXRITFMxeHVZU3BpYWtQUFJFVFAtaW1hZ2VzXzE3ODExNzkzMTM2OTRfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyWnBaM1Z5WlY5emFXMTFiR0YwYVc5dS5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=kF2JPjSk8Vf9LOM57GUPvB-0gq-zGdCCX5WKnEtkDx0gVQ0HpK4iKulE7s51tsdzWyfkslSf6c1wPfm2YAiZ9-7nQLHJqJ16721xip98Iq140VMzmf7wMfQ9uUqX-E-9UAx41xVHMw6YVEP3nW8GUdwluz5bH3JYj9wEocb9x5voKrGbPQTWqgHvAj6uXo5cKhBQQuHaPmX~Yn-uK9y0vFlb25Iwk3Fu7ZbkU8KPW-qGWoF6BK7oSfqEbEav2SZQEnfqSdPpCCORvZW8LNNy3tyunePsMZxEkrFSBAw9uf6ewgIVgsaMXZh5TjlJwfX1AYK8CcCyqZXBg3w9UEshnQ__)
*Figure 1: Interface de simulation unitaire et courbe prévisionnelle des ventes.*

Cette figure met en évidence une **courbe de ventes dynamique** caractérisée par des pics récurrents, qui sont typiques de la **saisonnalité hebdomadaire** observée dans le commerce de détail. Le panneau de configuration situé à gauche de l'interface offre la possibilité d'ajuster des variables clés telles que l'ID du magasin, son type, l'assortiment de produits, la distance par rapport aux concurrents, et la date de début de la projection. Cette fonctionnalité démontre la **flexibilité du modèle** à simuler divers scénarios et à évaluer l'impact de différents facteurs sur les ventes, offrant ainsi un outil puissant pour l'analyse 
prévisionnelle et la prise de décision stratégique.

### 3.2. Chiffre d'Affaires Projeté (Prévision Future)

La deuxième visualisation (Figure 2) présente une projection du chiffre d'affaires sur un horizon de 120 jours, intégrant des intervalles d'incertitude. Cette représentation est cruciale pour la planification stratégique, car elle offre une perspective plus complète des ventes futures potentielles et des risques associés.

![Chiffre d'Affaires Projeté (Prochains 120 jours)](https://private-us-east-1.manuscdn.com/sessionFile/zhTMAjfnt5eBFUykE4Y1Kl/sandbox/5UItHLS1xuYSpiakPPRETP-images_1781179313694_na1fn_L2hvbWUvdWJ1bnR1L2ZpZ3VyZV9wcm9qZWN0aW9u.png?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wcml2YXRlLXVzLWVhc3QtMS5tYW51c2Nkbi5jb20vc2Vzc2lvbkZpbGUvemhUTUFqZm50NWVCRlV5a0U0WTFLbC9zYW5kYm94LzVVSXRITFMxeHVZU3BpYWtQUFJFVFAtaW1hZ2VzXzE3ODExNzkzMTM2OTRfbmExZm5fTDJodmJXVXZkV0oxYm5SMUwyWnBaM1Z5WlY5d2NtOXFaV04wYVc5dS5wbmciLCJDb25kaXRpb24iOnsiRGF0ZUxlc3NUaGFuIjp7IkFXUzpFcG9jaFRpbWUiOjE3OTg3NjE2MDB9fX1dfQ__&Key-Pair-Id=K2HSFNDJXOU9YS&Signature=cj4dKSTc3umfwsABZ3JMprUtAj-SvnDxql9ZQ1kykX-N3og48bCfQwN1Wn1G7thKuDLjzapr6gCp-rY8WvHFiz26kXzz7PWQwbwiXPiDfLBrkocoE5aH2SayHFtsH92LXoBtEv-gGE3Z-wpKyK6-nHovB23JolobRs5M6b0Ysb6O3W0doIkTy6rjZnrLzZvYwaUbWJyBC-yKKMs0fk~tKY7CND0YGSBoAv~HsVR4nDVtehNB1pkDP1f4oJFAKyZEldPIqJoyOrYJR3EWTmr53Mq0H6y9oL-6QSjvMq5vk4U3BGhL8ew~0NyWClapuZNodnumlgXOFt1pEfaW7WP7iA__)
*Figure 2: Projection du chiffre d'affaires sur 120 jours avec intervalles d'incertitude.*

Cette figure illustre la **prévision des ventes** pour un magasin sélectionné sur une période de 120 jours, accompagnée d'une **bande d'incertitude** (représentée par la zone bleue claire). Les pics réguliers observés dans la courbe de prévision confirment la capacité du modèle à capturer et à projeter la **saisonnalité des ventes**. L'inclusion de l'intervalle d'incertitude est une caractéristique fondamentale, car elle fournit une estimation de la plage dans laquelle les ventes réelles sont susceptibles de se situer. Cela aide considérablement à la **gestion des risques** et à la prise de décisions plus éclairées, permettant aux gestionnaires d'anticiper les variations et d'ajuster leurs stratégies en conséquence. Le panneau de gauche de l'interface permet de sélectionner le magasin et de définir l'horizon de prédiction, soulignant l'aspect **interactif et personnalisable** de l'outil, qui peut être adapté aux besoins spécifiques de chaque utilisateur.

## 4. Conclusion

Les visualisations présentées dans ce rapport démontrent l'efficacité du projet de prévision des ventes à transformer des données complexes en informations exploitables. L'application Streamlit offre une interface intuitive pour la simulation unitaire et la projection future, permettant aux utilisateurs de comprendre les dynamiques de ventes et de prendre des décisions éclairées. L'intégration des intervalles d'incertitude renforce la robustesse des prévisions, offrant une vue réaliste des scénarios possibles.

## Références

[1] rossmann_predictions_batch-1.csv
[2] une-version-Streamlit-API-pour-la-demonstration.pdf
[3] Notebook-Google-Colab-complet-Projet-Rossmann-St-1.pdf
[4] une-API-operationnelle-avec-le-meilleur-modele.pdf
