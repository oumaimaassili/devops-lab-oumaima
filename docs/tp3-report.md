# TP3 : Docker Networking et Docker Compose

**Étudiante :** Oumaima Assili
**Filière :** MPSRCC1
**Matière :** DevOps
**Enseignante de TP :** Mariem Jha
**Date :** 06/11/2026

---

## 1. Préparation (Partie 0)

Les anciens conteneurs du TP2 (`product-service`, `order-service`) ont été supprimés avec `docker stop` et `docker rm`. Les messages « No such container » confirment qu'ils n'existaient plus. `docker ps` ne liste plus aucun conteneur, donc les ports **8001** et **8002** sont libres.

Les anciens conteneurs bloquent ces ports car un port hôte ne peut être publié que par un seul conteneur à la fois.

## 2. Tâche 1 : Réseaux et DNS

| Réseau | Type | Driver | Subnet | Gateway |
|---|---|---|---|---|
| `bridge` | par défaut | bridge | 172.17.0.0/16 | 172.17.0.1 |
| `tp3-net` | défini par l'utilisateur | bridge | 172.22.0.0/16 | 172.22.0.1 |

- Un conteneur `tp3-web` (nginx:alpine) a été lancé sur `tp3-net`.
- `nslookup tp3-web` (depuis un conteneur busybox:1.36 sur `tp3-net`) a résolu le nom en adresse IP : le DNS du réseau personnalisé fonctionne.
- `docker network inspect tp3-net` montre `tp3-web` dans la section `Containers`.
- Nettoyage : `docker rm -f tp3-web` puis `docker network rm tp3-net`.

**Pourquoi un nom est plus fiable qu'une IP fixe ?** L'IP d'un conteneur change à chaque recréation, alors que son nom reste identique et le DNS Docker le résout toujours vers la bonne adresse.

## 3. Tâche 2 : compose.yaml

```yaml
services:
  product-service:
    build:
      context: .
      dockerfile: product-service/Dockerfile.reference
    ports:
      - "8001:8001"
    networks:
      - app-net

  order-service:
    build:
      context: .
      dockerfile: order-service/Dockerfile.reference
    ports:
      - "8002:8002"
    environment:
      PRODUCT_SERVICE_URL: http://product-service:8001
    depends_on:
      - product-service
    networks:
      - app-net

networks:
  app-net:
    driver: bridge
```

`docker compose config` valide la configuration : 2 services (`product-service`, `order-service`) et le réseau `app-net` (nommé `devops-microservices-tp2_app-net`), sans erreur YAML.

## 4. Tâche 3 : Déploiement et tests

**Déploiement :** `docker compose up -d --build` a construit les deux images (environ 5 minutes pour le premier build), créé le réseau `devops-microservices-tp2_app-net` et démarré les 2 conteneurs. `docker compose ps` les montre **Up**, avec les ports 8001 et 8002 publiés. Les logs confirment le démarrage d'Uvicorn pour les deux services.

**Tests HTTP :**

| Requête | Résultat |
|---|---|
| `GET localhost:8001/health` | `{"status":"ok","service":"product-service"}` |
| `GET localhost:8001/products` | Laptop (1200.0), Keyboard (80.0), Mouse (40.0) |
| `GET localhost:8002/health` | `{"status":"ok","service":"order-service"}` |
| `GET localhost:8002/orders` | `[]` (aucune commande) |

**Création d'une commande** (`product_id` = 1, `quantity` = 2) :

```
id           : 1
product_id   : 1
product_name : Laptop
quantity     : 2
total        : 2400.0
```

Le total est de 2400.0 (1200 × 2). Order Service a donc contacté Product Service via `http://product-service:8001`.

**DNS et réseau :**

- `docker network ls` montre `devops-microservices-tp2_app-net` (driver bridge).
- `docker compose exec order-service python -c "import socket; print(socket.gethostbyname('product-service'))"` affiche **172.21.0.2**.
- La résolution se fait par le nom de service, sans dépendre d'une IP fixe.

## 5. Tâche 4 : Panne et récupération

1. `docker compose stop product-service` : seul `order-service` reste **Up** dans `docker compose ps`.
2. `POST /orders` (product_id = 2, quantity = 1) pendant la panne : réponse **HTTP 500** (« Le serveur distant a retourné une erreur : (500) Erreur interne du serveur »). Les logs d'Order Service se terminent par `httpx.ConnectTimeout` : l'appel vers `http://product-service:8001/products/2` a expiré.
3. `docker compose start product-service`, puis nouvelle commande :

```
id           : 2
product_id   : 2
product_name : Keyboard
quantity     : 1
total        : 80.0
```

4. `GET /orders` liste les deux commandes (Laptop 2400.0 et Keyboard 80.0).

**Conclusion :** Order Service est un processus indépendant, il reste en cours d'exécution même quand sa dépendance est indisponible. Seules les requêtes qui ont besoin de Product Service échouent. Dès que Product Service redémarre, la création de commande refonctionne.

## 6. Nettoyage

`docker compose down` supprime les conteneurs et le réseau du projet. `docker compose ps` est vide et `devops-microservices-tp2_app-net` n'apparaît plus dans `docker network ls`. Le code source et les images construites sont conservés.

## 7. Réponses aux questions

**Q1. Bridge par défaut et bridge défini par l'utilisateur.**
Le bridge par défaut ne fournit pas de résolution DNS par nom entre conteneurs : il faut utiliser les IP. Le bridge défini par l'utilisateur fournit un DNS automatique (les conteneurs se joignent par leur nom) et isole mieux les conteneurs des autres réseaux.

**Q2. DNS par nom de service.**
Docker intègre un DNS interne qui résout, sur un réseau partagé, le nom d'un service vers l'IP de son conteneur. Order Service utilise `http://product-service:8001` car l'IP d'un conteneur peut changer, alors que le nom du service reste stable.

**Q3. Contenu de compose.yaml.**
- `services` : liste les conteneurs de l'application.
- `build` : indique le contexte et le Dockerfile pour construire l'image.
- `ports` : publie un port de l'hôte vers le conteneur (`8001:8001`).
- `environment` : passe la configuration à l'exécution (`PRODUCT_SERVICE_URL`).
- `networks` : rattache les services au réseau partagé `app-net`.

**Q4. Pourquoi le contexte de build est `.`.**
Les `Dockerfile.reference` copient des fichiers avec des chemins relatifs à la racine du projet (par exemple `product-service/app.py`). Le contexte doit donc être la racine `.`, sinon les `COPY` échouent.

**Q5. `up -d`, `stop` et `down`.**
`up -d` crée et démarre les conteneurs en arrière-plan. `stop` arrête les conteneurs sans les supprimer. `down` arrête et supprime les conteneurs et le réseau du projet. Il ne supprime ni le code source ni, par défaut, les images construites.

**Q6. Rôle et limite de `depends_on`.**
`depends_on` définit l'ordre de démarrage : Order Service démarre après Product Service. Sa limite est qu'il n'attend pas que l'application soit prête à répondre en HTTP, seulement que le conteneur soit démarré. Pour attendre la disponibilité, il faut un `healthcheck` avec `condition: service_healthy`.

**Q7. Que se passe-t-il quand Product Service s'arrête.**
Order Service reste Up car c'est un conteneur indépendant, mais ses appels vers Product Service échouent : `ConnectTimeout` dans les logs et HTTP 500 renvoyé au client. Après le redémarrage de Product Service, les commandes fonctionnent à nouveau.

**Q8. Vérifier le DNS et inspecter le réseau.**
- DNS : `docker compose exec order-service python -c "import socket; print(socket.gethostbyname('product-service'))"` (résultat : 172.21.0.2).
- Réseau : `docker network ls` puis `docker network inspect devops-microservices-tp2_app-net`.

## 8. Limites

- Order Service ne gère pas l'erreur de connexion : il renvoie un 500 au lieu d'un 502/503 explicite.
- Pas de `healthcheck` : `depends_on` seul ne garantit pas que Product Service est prêt.
- Aucun mécanisme de nouvelle tentative (retry) côté Order Service.