# Selenium WebDriver — L'essentiel

Ce support vous fait construire, à partir d'un dossier vide, une suite de tests Selenium en Python pour le back-office d'EventFlow. Vous commencerez par des tests simples, écrits directement avec Selenium : ouvrir une page, trouver des éléments, remplir un formulaire, attendre la réponse de l'application. Vous réorganiserez ensuite ces tests avec le **Page Object Model**, l'architecture la plus répandue dans les projets d'automatisation d'interface.

À la fin, vous devez être capable de :

- créer et configurer un projet Selenium avec pytest ;
- trouver des éléments avec des sélecteurs CSS et quelques expressions XPath ;
- remplir et envoyer un formulaire, lire ce qu'affiche la page ;
- attendre correctement une application React, sans `time.sleep` ;
- lire un tableau HTML, créer et désactiver une donnée ;
- écrire des Page Objects qui héritent d'une classe de base ;
- composer des fixtures pytest ;
- ajouter un scénario à une suite existante ;
- obtenir une capture d'écran à chaque échec, et traiter les listes déroulantes, les alertes, les cadres, les onglets et la souris.

Le projet final :

```text
selenium_eventflow/
    requirements.txt
    pytest.ini
    config.py              URL des sites testés et comptes de test
    conftest.py            fixtures driver et orga_driver, capture en cas d'échec
    captures/              créé automatiquement au premier échec
    pages/
        __init__.py
        base_page.py       BasePage : ce qui est commun à toutes les pages
        login_page.py      LoginPage
        promos_page.py     PromosPage
    tests/
        test_navigation.py
        test_locators_login.py
        test_connexion.py
        test_promos.py
        test_outils.py     boîte à outils, sur un site d'entraînement
```

Chaque fichier est créé au moment où il devient utile. Les indices des exercices sont repliés : ouvrez-les après avoir cherché.

## Les comptes de démonstration

| Rôle | Email | Mot de passe |
|---|---|---|
| Organisateur | `orga@eventflow.test` | `orga1234` |
| Client | `client@eventflow.test` | `client1234` |

L'organisateur a accès au back-office (`/admin`), le client non.

---

## 1. Installer Selenium et créer le projet

### 1.1 Démarrer EventFlow

À la racine du dépôt EventFlow :

```bash
docker compose up -d --build
```

L'application est disponible sur http://localhost:5173. Pour repartir des données de démonstration d'origine :

```bash
docker compose down -v
docker compose up -d --build
```

### 1.2 Créer le projet

Le projet de tests est indépendant de l'application. Créez un dossier `selenium_eventflow/` à côté du dépôt EventFlow, puis, **depuis ce dossier**, un environnement virtuel :

```powershell
# Windows PowerShell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Si PowerShell refuse d'exécuter le script d'activation, autorisez les scripts locaux pour votre utilisateur, puis relancez l'activation :

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Créez `requirements.txt` :

```text
selenium>=4.20
pytest>=8.0
```

et installez :

```bash
pip install -r requirements.txt
```

Il faut aussi que Google Chrome soit installé. Au premier lancement, Selenium télécharge lui-même le programme `chromedriver` qui correspond à votre version de Chrome (c'est le rôle de **Selenium Manager**) : la machine doit avoir accès à Internet à ce moment-là.

Toutes les commandes de ce support se lancent depuis `selenium_eventflow/`, environnement virtuel activé.

### 1.3 Ce que fait Selenium

```text
votre test Python  ──>  chromedriver  ──>  Chrome
```

La bibliothèque `selenium` envoie des commandes (ouvrir une URL, trouver un élément, cliquer) à `chromedriver`, qui les fait exécuter par un vrai Chrome. Par rapport à Playwright, quatre différences comptent :

- **le navigateur est à votre charge** : il faut le créer, le configurer et le fermer ;
- **il n'y a pas d'attente automatique** : Selenium cherche un élément au moment où vous le demandez, même s'il n'est pas encore affiché ;
- **on cherche un élément par une stratégie et une valeur** (un sélecteur CSS, une expression XPath), sans `getByRole` ni `getByLabel` ;
- **les vérifications sont des `assert` pytest**, qu'on écrit après avoir attendu.

---

## 2. La fixture `driver`, Chrome et la navigation

### 2.1 Un premier test, et son défaut

Créez un dossier `tests/`, puis `tests/test_navigation.py` :

```python
from selenium import webdriver


def test_page_de_connexion_s_ouvre():
    driver = webdriver.Chrome()
    driver.get("http://localhost:5173/login")

    assert driver.current_url == "http://localhost:5173/login"

    driver.quit()
```

```bash
pytest tests/test_navigation.py
```

- `webdriver.Chrome()` démarre Chrome ; l'objet `driver` représente le navigateur.
- `driver.get(url)` ouvre une page. `driver.current_url` renvoie l'URL affichée, `driver.title` le titre de l'onglet.
- `driver.quit()` ferme Chrome.

Si l'`assert` échoue, `driver.quit()` n'est jamais exécuté, et Chrome reste ouvert. Après vingt tests en échec, vingt navigateurs tournent en arrière-plan.

### 2.2 La fixture `driver`

La création et la fermeture du navigateur sont une préparation de test : elles ont leur place dans une fixture `yield`, dont la partie après le `yield` s'exécute **même si le test échoue**. Créez `conftest.py` **à la racine du projet** :

```python
import os

import pytest
from selenium import webdriver


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    if os.getenv("HEADLESS", "true").lower() == "true":
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")

    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()
```

- pytest lit automatiquement les fichiers `conftest.py`. Placé à la racine, celui-ci fournit la fixture `driver` à tous les tests du dossier `tests/`, sans import.
- `--headless=new` fait tourner Chrome sans fenêtre : indispensable sur un serveur d'intégration continue, et plus rapide.
- `--window-size=1366,900` fixe la taille de la fenêtre. En headless, elle est petite par défaut, et la mise en page d'EventFlow change selon la largeur.
- La fixture a le scope par défaut, `function` : chaque test reçoit un Chrome neuf, sans session ni données d'un test précédent.

Dans certains conteneurs ou serveurs d'intégration continue sous Linux, Chrome refuse de démarrer sans l'option `--no-sandbox`. Elle désactive une protection du navigateur : on ne l'ajoute que dans ces environnements, pas sur un poste de travail.

**Voir le navigateur.** Par défaut, les tests tournent sans fenêtre. Pour regarder ce qui se passe :

```powershell
$env:HEADLESS = "false"         # Windows PowerShell, jusqu'à la fermeture du terminal
pytest
Remove-Item Env:HEADLESS        # revenir au mode par défaut
```

```bash
HEADLESS=false pytest           # macOS / Linux, pour une commande
```

### 2.3 La configuration : `config.py` et `pytest.ini`

L'URL de l'application va se retrouver dans tous les tests. Si l'application tourne ailleurs, il faudrait modifier chaque fichier. On la range dans `config.py`, à la racine :

```python
"""Configuration du projet de tests, lue dans les variables d'environnement."""
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:5173").rstrip("/")
```

`os.getenv("BASE_URL", ...)` lit une variable d'environnement, avec une valeur par défaut pour travailler en local. `.rstrip("/")` retire une éventuelle barre oblique finale.

Pour que les tests, rangés dans `tests/`, puissent faire `import config`, Python doit chercher les modules à la racine du projet. On le déclare dans `pytest.ini`, à la racine :

```ini
[pytest]
testpaths = tests
pythonpath = .
```

- `testpaths = tests` : `pytest` lancé sans argument cherche les tests dans `tests/`.
- `pythonpath = .` : la racine du projet est ajoutée au chemin d'import.

Le test s'écrit alors :

```python
import config


def test_page_de_connexion_s_ouvre(driver):
    driver.get(config.BASE_URL + "/login")
    ...
```

### Exercice 1 — Premiers tests

**Énoncé**

Dans `tests/test_navigation.py`, remplacez le premier test par deux tests qui utilisent la fixture et la configuration :

1. la page de connexion s'ouvre : titre `eventflow` et URL `.../login` ;
2. le catalogue s'ouvre : titre `eventflow` et URL `.../` (avec la barre oblique finale).

**Règles / étapes**

1. Créez `conftest.py`, `config.py` et `pytest.ini`.
2. Écrivez les tests, lancez-les en headless, puis en mode visible.
3. Lancez `pytest -v` : les noms des tests doivent dire ce qu'ils vérifient.

**Contraintes**

- aucune URL écrite en dur dans les tests ;
- aucun `quit()` dans les tests.

Si un test échoue avec `net::ERR_CONNECTION_REFUSED`, EventFlow n'est pas démarré.

---

## 3. Trouver les éléments et interagir

### 3.1 Ce qu'il y a dans la page

Le formulaire de la page `/login`, simplifié :

```html
<form>
  <div class="field">
    <label>Email</label>
    <input class="input" type="email">
  </div>
  <div class="field">
    <label>Mot de passe</label>
    <input class="input" type="password">
  </div>
  <button class="btn btn-primary">Se connecter</button>
</form>
```

Ce qu'on peut utiliser : les **balises** (`input`, `button`), les **attributs** (`type`, `class`), le **texte** affiché (`Se connecter`).

Ce qu'il ne faut pas supposer : EventFlow n'a **aucun** `id`, `name` ou `data-testid`, et ses labels ne sont pas reliés aux champs. Les textes de l'interface sont écrits **sans accents** : `Deconnexion`, `Creer`, `Desactiver`.

**Inspecter la page.** Dans Chrome, `F12` ouvre les DevTools. Dans l'onglet **Elements**, `Ctrl+F` accepte un sélecteur CSS ou une expression XPath et affiche le nombre de correspondances. Testez chaque locator ici avant de l'écrire dans un test.

### 3.2 `find_element`, `find_elements` et les locators

```python
from selenium.webdriver.common.by import By

EMAIL = (By.CSS_SELECTOR, "input[type=email]")

champ = driver.find_element(*EMAIL)          # le premier élément trouvé, ou une erreur
champs = driver.find_elements(*EMAIL)        # la liste des éléments trouvés, éventuellement vide
```

- Un **locator** est un tuple (stratégie, valeur). On le range dans une constante en majuscules.
- `*EMAIL` dépaquette le tuple : `find_element(*EMAIL)` équivaut à `find_element(By.CSS_SELECTOR, "input[type=email]")`.
- `find_element` lève `NoSuchElementException` si rien ne correspond. `find_elements` renvoie une liste vide : c'est l'outil pour compter, ou vérifier une absence.
- `find_element` renvoie le **premier** élément trouvé, sans signaler qu'il y en a d'autres. Un bon locator désigne **un seul** élément.

### 3.3 Les sélecteurs CSS

| Syntaxe | Sélectionne | Exemple |
|---|---|---|
| `balise` | une balise | `h1` |
| `.classe` | une classe | `.notice-err` |
| `balise.classe` | balise et classe | `h1.page-title` |
| `[attribut=valeur]` | un attribut | `input[type=password]` |
| `A B` | B à l'intérieur de A | `form button` |

Sur `/login`, quand on n'est pas connecté, `.btn-primary` correspond à **deux** éléments : le bouton du formulaire et le lien « Connexion » de la barre de navigation. `form button.btn-primary` lève l'ambiguïté.

### 3.4 Trois recettes XPath

CSS ne sait pas chercher un élément par son texte, ni passer d'un label à son champ. XPath le peut. Trois formes suffisent pour tout ce support :

```text
//button[normalize-space()='Se connecter']
```

« Un `button` dont le texte est `Se connecter` ». `normalize-space()` ignore les espaces en début et en fin, ce qui compte quand un élément contient une icône avant son texte.

```text
//label[normalize-space()='Mot de passe']/following-sibling::input
```

« L'`input` placé après le label `Mot de passe`, au même niveau ». C'est la façon de trouver un champ par son libellé quand le label n'est pas relié au champ.

```text
//tr[td[normalize-space()='WELCOME10']]
```

« La ligne de tableau `tr` qui contient une cellule `td` dont le texte est `WELCOME10` ». Elle servira au chapitre 6.

Toutes s'utilisent avec `By.XPATH`. Pour les liens, Selenium propose aussi `By.PARTIAL_LINK_TEXT`, qui cherche un `<a>` dont le texte contient une valeur :

```python
LIEN_BACK_OFFICE = (By.PARTIAL_LINK_TEXT, "Back-office")
```

**À éviter** : les chemins qui dépendent de la position, comme `/html/body/div[1]/div/div[2]/...` ou le « Copy XPath » des DevTools. Ils cassent dès qu'un élément est ajouté à la page.

### 3.5 Interagir et lire

```python
champ = driver.find_element(*EMAIL)
champ.clear()                                 # vider le champ
champ.send_keys("orga@eventflow.test")        # taper du texte
driver.find_element(*SUBMIT).click()          # cliquer

element.text                                  # le texte affiché
champ.get_attribute("value")                  # la valeur d'un champ de saisie
```

- `send_keys` **ajoute** du texte. La page de connexion arrive avec le compte client déjà saisi : sans `clear()`, on obtient `client@eventflow.testorga@eventflow.test`.
- `.text` est vide sur un champ de saisie ; sa valeur se lit avec `get_attribute("value")`.

### Exercice 2 — Les locators de la page de connexion

**Énoncé**

Vérifiez que cinq locators de la page de connexion désignent chacun exactement un élément.

**Règles / étapes**

1. Dans les DevTools, trouvez un locator pour : le champ email, le champ mot de passe, le bouton « Se connecter ». Pour le bouton, écrivez une version CSS et une version XPath par le texte. Pour le mot de passe, écrivez aussi une version XPath par le label.
2. Créez `tests/test_locators_login.py`, avec une liste `LOCATORS` de ces cinq tuples.
3. Écrivez **un** test paramétré qui ouvre `/login` et vérifie, pour chaque locator, que `find_elements` renvoie exactement un élément.

**Contraintes**

- les cas paramétrés ont des identifiants lisibles dans `pytest -v` ;
- le message d'assertion affiche le nombre d'éléments trouvés.

<details>
<summary>Indice</summary>

`ids=lambda loc: loc[1]` donne à chaque cas la valeur du locator comme identifiant.

</details>

### Exercice 3 — Un mauvais mot de passe

**Énoncé**

Un organisateur saisit son email et un mot de passe incorrect. La page doit afficher le message `Incorrect email or password` et rester sur `/login`.

**Règles / étapes**

1. Provoquez l'erreur à la main dans votre navigateur et trouvez l'élément qui porte le message.
2. Créez `tests/test_connexion.py` et écrivez le test : ouvrir `/login`, vider et remplir les deux champs, cliquer, lire le message, vérifier le texte et l'URL. Écrivez l'adresse email directement dans le test : les identifiants seront rangés dans `config.py` plus loin.
3. Lancez-le plusieurs fois. Notez l'exception obtenue et la ligne qui la lève.

Ne cherchez pas à le corriger : c'est l'objet du chapitre suivant.

<details>
<summary>Indice</summary>

Le message est dans un `div` qui porte la classe `notice-err`.

</details>

---

## 4. Attendre l'application : `WebDriverWait`

### 4.1 Ce qui se passe après un clic

```text
clic sur "Se connecter"
  ├─ React envoie la requête à l'API          ← le test continue ici
  ├─ l'API répond (quelques millisecondes,     et cherche le message :
  │  ou plusieurs secondes)                     il n'existe pas encore
  └─ React affiche le message
```

`click()` rend la main dès que le clic est fait. `find_element` cherche dans la page **à cet instant** : `NoSuchElementException`. Le même décalage existe après `driver.get()` : la page se charge, puis React demande ses données à l'API et les affiche.

**`time.sleep(2)` n'est pas une solution.** Deux secondes suffisent sur votre poste, pas forcément sur un serveur chargé : le test devient instable. Et si la réponse arrive en 50 millisecondes, le test attend quand même deux secondes, à chaque exécution.

Selenium propose aussi une attente « implicite » (`driver.implicitly_wait(5)`), qui fait réessayer chaque recherche. Elle n'attend que l'existence des éléments, pas leur visibilité ni le changement d'une URL, et elle produit des durées imprévisibles quand on la combine avec des attentes explicites. Ce support ne l'utilise pas.

### 4.2 Les attentes explicites

```python
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

wait = WebDriverWait(driver, 10)
message = wait.until(EC.visibility_of_element_located(ERREUR))
```

- `until` vérifie la condition toutes les demi-secondes. Dès qu'elle est vraie, il **renvoie** sa valeur et le test continue ; au bout de 10 secondes, il lève une `TimeoutException`.
- Le délai est un maximum : si l'élément apparaît en 200 millisecondes, le test attend 200 millisecondes.

Les conditions les plus utiles :

| Condition | Vraie quand | Pour |
|---|---|---|
| `EC.visibility_of_element_located(locator)` | l'élément est affiché (renvoie l'élément) | lire un texte, remplir un champ |
| `EC.element_to_be_clickable(locator)` | l'élément est affiché et actif (renvoie l'élément) | cliquer |
| `EC.url_contains("/admin")` | l'URL contient le texte | après une navigation |
| `EC.text_to_be_present_in_element(locator, "inactif")` | le texte de l'élément contient la valeur | attendre un changement d'état |
| `EC.presence_of_element_located(locator)` | l'élément existe dans la page, même caché (renvoie l'élément) | compter, lire un attribut |
| `EC.invisibility_of_element_located(locator)` | l'élément est caché ou absent | attendre la disparition d'un indicateur de chargement |

Les deux dernières reviennent au chapitre 13.

Quand aucune condition ne convient, on en écrit une avec une `lambda` : une fonction qui reçoit le navigateur et renvoie vrai quand l'état attendu est atteint.

```python
wait.until(lambda d: not d.current_url.endswith("/login"))
```

**La règle** : la première interaction avec une page passe par une attente, et chaque étape qui dépend d'une réponse de l'application attend l'état qui prouve que cette réponse est arrivée.

### Exercice 4 — Attendre le message d'erreur

1. Corrigez le test de l'exercice 3 : remplacez la lecture immédiate du message par une attente explicite adaptée. Attendez aussi le champ email avant de le remplir.
2. Lancez le test cinq fois.
3. Dans le test de l'exercice 2, ajoutez une attente sur le champ email juste après l'ouverture de la page. Sans elle, le test peut échouer de temps en temps avec une liste vide, si la page n'est pas encore affichée au moment du comptage.

<details>
<summary>Indice</summary>

On va lire le texte du message : il doit être affiché, pas seulement présent.

</details>

---

## 5. Les tests de connexion

### 5.1 Quand la connexion est-elle terminée ?

Une connexion réussie se déroule en plusieurs étapes : l'API renvoie un jeton, le navigateur l'enregistre, l'application charge le profil, puis affiche la barre de navigation de l'utilisateur connecté. Si le test ouvre `/admin` juste après le clic, avant la fin de ces étapes, l'application ne voit aucun utilisateur et renvoie vers `/login`.

Le signe fiable que la connexion est terminée : le bouton « Deconnexion » de la barre de navigation est affiché.

```python
DECONNEXION = (By.XPATH, "//button[normalize-space()='Deconnexion']")
```

Les pages du back-office ont toutes un titre `h1` de classe `page-title` (« Back-office » pour le tableau de bord). Il n'apparaît qu'une fois la session vérifiée.

### Exercice 5 — L'organisateur accède au back-office

**Énoncé**

Un organisateur se connecte, clique sur le lien « Back-office » de la barre de navigation, et arrive sur la page dont le titre est « Back-office ».

**Règles / étapes**

Dans `tests/test_connexion.py` :

1. remplir et envoyer le formulaire avec le compte organisateur ;
2. attendre la fin de la connexion ;
3. attendre que le lien « Back-office » soit cliquable, cliquer ;
4. attendre que l'URL contienne `/admin` ;
5. attendre le titre de la page et vérifier son texte.

Pour les identifiants, ajoutez à `config.py` les comptes de démonstration :

```python
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL", "client@eventflow.test")
CLIENT_PASSWORD = os.getenv("CLIENT_PASSWORD", "client1234")
ORGA_EMAIL = os.getenv("ORGA_EMAIL", "orga@eventflow.test")
ORGA_PASSWORD = os.getenv("ORGA_PASSWORD", "orga1234")
```

**Contraintes**

- aucun `time.sleep` ;
- identifiants lus dans `config`.

### Exercice 6 — Un client ne peut pas entrer dans le back-office

**Énoncé**

Un client connecté qui ouvre `/admin` est renvoyé vers le catalogue (`/`), et sa barre de navigation n'a pas de lien « Back-office ».

**Règles / étapes**

1. Connectez-vous avec le compte client, attendez la fin de la connexion.
2. Ouvrez `/admin` avec `driver.get`.
3. Attendez que l'URL ne se termine plus par `/admin`, avec une `lambda`.
4. Vérifiez l'URL finale et l'absence du lien avec `find_elements`.

**Question** : pourquoi la vérification d'absence doit-elle venir après l'attente de la redirection ?

---

## 6. Les codes promo

La page `/admin/promos` liste les codes promo et permet d'en créer.

### 6.1 Lire un tableau

```html
<table class="table">
  <tbody>
    <tr>
      <td class="mono">WELCOME10</td>
      <td>-10%</td>
      <td>0/1000</td>
      <td>23 janv. 2027</td>
      <td><span class="badge">actif</span></td>
      <td><button>Desactiver</button></td>
    </tr>
    <tr>
      <td class="mono">EXPIRED</td>
      <td>-15%</td>
      <td>0/100</td>
      <td>24 oct. 2026</td>
      <td><span class="badge">inactif</span></td>
      <td></td>
    </tr>
  </tbody>
</table>
```

Chaque `tr` est une ligne, chaque `td` une cellule. Un code inactif n'a pas de bouton « Desactiver ».

**Lire une colonne** : les codes sont dans les cellules de classe `mono`.

```python
CELLULES_CODE = (By.CSS_SELECTOR, "table.table tbody td.mono")
codes = [cellule.text for cellule in driver.find_elements(*CELLULES_CODE)]
```

**Trouver une ligne par son contenu**, puis chercher **à l'intérieur** de cette ligne :

```python
ligne = driver.find_element(By.XPATH, "//tr[td[normalize-space()='WELCOME10']]")
statut = ligne.find_element(By.CSS_SELECTOR, ".badge").text
cellules = [cellule.text for cellule in ligne.find_elements(By.TAG_NAME, "td")]
```

`find_element` et `find_elements` existent aussi sur un élément : ils cherchent alors dans ses descendants seulement. Attention au XPath : une expression qui commence par `//` cherche toujours **dans toute la page**, même appelée depuis une ligne. Pour chercher dans la ligne, il faut un point au début :

```python
ligne.find_elements(By.XPATH, "//button")    # tous les boutons de la page
ligne.find_elements(By.XPATH, ".//button")   # les boutons de cette ligne
```

**La ligne d'attente.** Tant que l'API n'a pas répondu, le tableau contient une seule ligne : « Aucun code promo. ». Attendre « une ligne du tableau » serait donc satisfait trop tôt. On attend une cellule `td.mono`, qui n'existe que dans les vraies données.

### 6.2 Le formulaire de création

```html
<form>
  <div class="field"><label>Code</label><input placeholder="SUMMER20"></div>
  <div class="field"><label>Reduction (%)</label><input type="number" max="100"></div>
  <div class="field"><label>Usages max</label><input type="number"></div>
  <button class="btn btn-primary">Creer</button>
</form>
```

Les champs se trouvent par leur label, avec la deuxième recette XPath. `Reduction (%)` et `Usages max` sont **préremplis** avec `10` et `100`.

Après une création réussie, une nouvelle ligne apparaît : le code, `-15%`, `0/20`, un tiret `—` (pas d'expiration) et le statut `actif`.

**Un champ prérempli qui résiste à `clear()`.** EventFlow est construit avec React, qui garde sa propre copie de la valeur de chaque champ. `clear()` vide le champ à l'écran sans toujours prévenir React : à la frappe suivante, React remet l'ancienne valeur, et le texte tapé s'y ajoute. Sur le champ `Reduction (%)`, on peut ainsi obtenir `1015` au lieu de `15`. Cela arrive surtout sur une machine lente : votre test peut passer chez vous et échouer ailleurs.

La parade : vider le champ aussi au clavier, en sélectionnant tout puis en supprimant. Ces frappes passent par les mêmes événements que celles d'un utilisateur.

```python
from selenium.webdriver.common.keys import Keys

champ.clear()
champ.send_keys(Keys.CONTROL, "a")    # Keys.COMMAND sur macOS
champ.send_keys(Keys.DELETE)
champ.send_keys("15")
```

### 6.3 Des données uniques

Deux codes ne peuvent pas porter le même nom. Un test qui crée toujours `ETE2027` passe une fois, puis échoue à chaque relance. On génère un code différent à chaque exécution :

```python
import uuid

code = "SEL" + uuid.uuid4().hex[:6].upper()    # par exemple 'SELA3F9C2'
```

Le préfixe permet de reconnaître les codes créés par les tests. En fin de test, on **désactive** le code créé : EventFlow ne permet pas de supprimer un code, mais un code désactivé ne peut plus servir.

### 6.4 Attendre un changement d'état

Après un clic sur « Desactiver », le badge affiche encore `actif` le temps que l'application recharge la liste. On attend que son texte contienne `inactif` :

```python
badge = (By.XPATH, f"//tr[td[normalize-space()='{code}']]//span[contains(@class,'badge')]")
wait.until(EC.text_to_be_present_in_element(badge, "inactif"))
```

Le locator vise la ligne **par son code** : il reste valable même si React a reconstruit la ligne entre-temps. Un élément trouvé **avant** la reconstruction, lui, ne correspond plus à rien dans la page : l'utiliser lève une `StaleElementReferenceException` (« élément périmé »). Le remède : chercher l'élément de nouveau, au moment où on en a besoin.

### Exercice 7 — Lire les codes promo

**Énoncé**

Créez `tests/test_promos.py` avec deux tests, après connexion de l'organisateur sur `/admin/promos` :

1. les codes `WELCOME10`, `VIP25` et `EXPIRED` sont listés ;
2. un test paramétré : `WELCOME10` est `actif` et a un bouton « Desactiver » ; `EXPIRED` est `inactif` et n'en a pas.

**Règles / étapes**

1. Écrivez dans le fichier une fonction `ouvrir_codes_promo(driver)` : connexion de l'organisateur, ouverture de la page, attente des vraies données.
2. Écrivez les deux tests.

**Contraintes**

- le premier test vérifie la présence des trois codes, pas le nombre de lignes : d'autres codes peuvent exister ;
- le bouton est cherché dans la ligne du code, pas dans toute la page.

<details>
<summary>Indice</summary>

Paramétrez le statut attendu **et** le nombre de boutons attendu (`1` ou `0`).

</details>

### Exercice 8 — Créer puis désactiver un code

**Énoncé**

Un organisateur crée un code unique avec une réduction de 15 % et 20 usages maximum. Le code apparaît avec les bonnes informations. Il le désactive : le code passe à `inactif` et n'a plus de bouton.

**Règles / étapes**

1. Générez un code unique.
2. Remplissez les trois champs en tenant compte des valeurs préremplies, puis cliquez sur « Creer ».
3. Attendez la ligne du code et vérifiez ses cinq premières cellules.
4. Cliquez sur « Desactiver » dans cette ligne, attendez le changement de statut.
5. Vérifiez le statut et l'absence de bouton.
6. Lancez le test trois fois de suite.

**Contraintes**

- le code est généré, jamais écrit en dur ;
- aucun `time.sleep`.

<details>
<summary>Indice 1</summary>

La séquence « vider, tout sélectionner, supprimer, taper » revient trois fois : une petite fonction `saisir(driver, locator, texte)` dans le fichier de tests évite de la répéter.

</details>

<details>
<summary>Indice 2</summary>

Le bouton « Creer » se trouve par son texte, à l'intérieur du formulaire : `//form//button[normalize-space()='Creer']`.

</details>

---

## 7. Le problème de la duplication

Relisez `tests/test_connexion.py` et `tests/test_promos.py`.

- **La connexion est écrite plusieurs fois** : chaque test de connexion ouvre `/login`, attend, vide et remplit deux champs, clique. `ouvrir_codes_promo` le refait.
- **Les locators sont recopiés** : `EMAIL`, `PASSWORD`, `SUBMIT`, `DECONNEXION` sont déclarés en haut des deux fichiers.
- **La saisie robuste n'existe qu'à un endroit** : `saisir` est dans `test_promos.py`, mais les tests de connexion utilisent encore `clear()` seul.
- **Les tests contiennent des détails d'interface** : XPath de lignes, classes CSS, attentes. Pour comprendre ce qu'un test vérifie, il faut lire comment il trouve chaque élément.

Supposez que les développeurs remplacent le bouton « Se connecter » par un bouton placé hors du formulaire. Il faut modifier le locator dans deux fichiers, et le premier oublié fait échouer des tests qui ne portent pas sur la connexion.

Le **Page Object Model** répond à ces problèmes :

- **une classe par page**, qui contient ses locators et les actions qu'on peut y faire ;
- les actions **attendent** ce qu'il faut pour être terminées ;
- les **tests** n'utilisent que les méthodes des pages, et contiennent les assertions.

À la fin du chapitre 11, le test de création s'écrira :

```python
def test_creation_puis_desactivation_d_un_code(orga_driver):
    code = "SEL" + uuid.uuid4().hex[:6].upper()
    page = PromosPage(orga_driver).ouvrir()

    page.creer(code, 15, 20)
    assert page.cellules(code)[:5] == [code, "-15%", "0/20", "—", "actif"]

    page.desactiver(code)
    assert page.statut(code) == "inactif"
```

### Exercice 9 — Repérer la duplication

Dans vos fichiers de tests, listez :

1. chaque endroit où la connexion est écrite ;
2. chaque locator déclaré dans plus d'un fichier ;
3. pour chaque test de `test_promos.py`, les lignes qui décrivent **ce que fait l'utilisateur** et celles qui décrivent **comment Selenium le fait**.

Gardez cette liste : elle sert de plan pour les chapitres suivants.

---

## 8. Les classes Python et `LoginPage`

### 8.1 Une classe, des objets

Une **classe** est un modèle ; un **objet** est une valeur construite à partir de ce modèle. Vous en utilisez déjà : `driver` est un objet de la classe `webdriver.Chrome`, et `WebDriverWait(driver, 10)` crée un objet.

```python
class LoginPage:
    def __init__(self, driver):
        self.driver = driver


page = LoginPage(driver)      # crée un objet LoginPage
page.driver                   # le navigateur, rangé dans l'objet
```

- `__init__` est le **constructeur** : Python l'appelle automatiquement à la création de l'objet, avec les arguments donnés.
- `self` désigne **l'objet lui-même**. Python le passe automatiquement en premier argument : on ne l'écrit pas à l'appel.
- `self.driver = driver` range le navigateur dans l'objet. On l'appelle un **attribut**.

### 8.2 Les méthodes

Une **méthode** est une fonction définie dans la classe. Son premier paramètre est toujours `self`, qui lui donne accès aux attributs :

```python
class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "input[type=email]")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def ouvrir(self):
        self.driver.get(config.BASE_URL + "/login")
        self.wait.until(EC.visibility_of_element_located(self.EMAIL))
        return self


page = LoginPage(driver)
page.ouvrir()
```

- `EMAIL` est défini dans le corps de la classe, hors de toute méthode : c'est un **attribut de classe**, partagé par tous les objets `LoginPage`. C'est la place des locators. Les méthodes y accèdent par `self.EMAIL`.
- Le `WebDriverWait` est créé une fois, dans le constructeur, et rangé dans `self.wait`.
- `ouvrir` renvoie `self`, c'est-à-dire la page elle-même. On peut alors enchaîner : `LoginPage(driver).ouvrir().soumettre(...)`.

### 8.3 De la fonction à la méthode

```python
# avant : une fonction
def saisir(driver, locator, texte):
    champ = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(locator))
    ...

saisir(driver, EMAIL, "orga@eventflow.test")


# après : une méthode
class LoginPage:
    def saisir(self, locator, texte):
        champ = self.wait.until(EC.visibility_of_element_located(locator))
        ...

page.saisir(page.EMAIL, "orga@eventflow.test")
```

Le paramètre `driver`, qu'on transmettait à chaque appel, est devenu un attribut de l'objet, donné **une fois** à la création.

### 8.4 Les règles d'une page

1. **Aucune assertion dans une page.** Une page agit et lit ; le test décide si le résultat est correct.
2. **Les méthodes portent le nom d'une intention** : `se_connecter`, `desactiver`, et non `cliquer_sur_le_bouton`.
3. **Une action attend ce qu'il faut pour être terminée.** `se_connecter` ne rend la main qu'une fois la session ouverte.
4. **Une action qui reste sur la page renvoie `self`. Une lecture renvoie la valeur lue** (un texte, une liste, un nombre).

Pour que les tests puissent importer les pages, créez un dossier `pages/` à la racine, avec un fichier vide `pages/__init__.py`. Ce fichier fait de `pages` un paquet Python : `from pages.login_page import LoginPage` fonctionne depuis tous les tests, grâce à `pythonpath = .`.

### Exercice 10 — `LoginPage`

**Énoncé**

Créez `pages/login_page.py` avec une classe `LoginPage`, et réécrivez avec elle le test du mauvais mot de passe.

**Règles / étapes**

1. Attributs de classe : `EMAIL`, `PASSWORD`, `SUBMIT`, `ERREUR`, `DECONNEXION`.
2. Constructeur : `self.driver` et `self.wait`.
3. Méthodes :
   - `trouver(locator)` : attend qu'un élément soit visible et le renvoie ;
   - `cliquer(locator)` : attend qu'un élément soit cliquable et clique ;
   - `saisir(locator, texte)` : la saisie robuste du chapitre 6 ;
   - `ouvrir()` ;
   - `soumettre(email, password)` : remplit et envoie le formulaire, **sans rien attendre ensuite** ;
   - `se_connecter(email, password)` : soumet, puis attend le bouton « Deconnexion » ;
   - `message_erreur()` : attend le message et renvoie son texte.
4. Réécrivez `test_mauvais_mot_de_passe_affiche_une_erreur`.

**Contraintes**

- le test réécrit ne contient ni locator, ni attente, ni `find_element` ;
- `ouvrir`, `soumettre` et `se_connecter` renvoient `self`.

<details>
<summary>Indice 1</summary>

Le test réécrit tient en trois lignes : créer et ouvrir la page en soumettant le mauvais mot de passe, puis deux `assert`.

</details>

<details>
<summary>Indice 2</summary>

Pourquoi deux méthodes, `soumettre` et `se_connecter` ? Le test du mauvais mot de passe ne peut pas utiliser une méthode qui attend une connexion réussie : elle échouerait au bout de dix secondes.

</details>

---

## 9. Une classe de base : `BasePage`

### 9.1 L'héritage

La page des codes promo aura besoin de `trouver`, `cliquer`, `saisir`... exactement comme `LoginPage`. Plutôt que de recopier ces méthodes dans chaque page, on les place dans une classe de base dont les pages **héritent** :

```python
class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def trouver(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))


class LoginPage(BasePage):
    EMAIL = (By.CSS_SELECTOR, "input[type=email]")

    def ouvrir(self):
        self.driver.get(config.BASE_URL + "/login")
        self.trouver(self.EMAIL)
        return self
```

- `class LoginPage(BasePage)` : `LoginPage` hérite de `BasePage`. Elle reçoit son constructeur et toutes ses méthodes.
- `LoginPage(driver)` appelle le constructeur de `BasePage` : l'objet a bien `self.driver` et `self.wait`.
- Dans `ouvrir`, `self.trouver(...)` appelle la méthode héritée.

### 9.2 Ce qui va dans `BasePage`

`BasePage` contient ce qui sert à **toutes** les pages :

- le navigateur et l'attente (`__init__`) ;
- les actions élémentaires : `attendre(condition)`, `trouver`, `cliquer`, `saisir`, `texte(locator)` ;
- `champ(libelle)`, qui renvoie le locator d'un champ par son label : tous les formulaires d'EventFlow ont la même structure ;
- les éléments présents sur toutes les pages : la **barre de navigation** (lien « Back-office », bouton « Deconnexion ») et le titre `h1.page-title` des pages du back-office, avec les méthodes `aller_au_back_office()`, `a_le_lien_back_office()` et `titre()`.

Ce qui est propre à une page reste dans sa classe : les champs du formulaire de connexion dans `LoginPage`, le tableau des codes dans `PromosPage`.

La barre de navigation est un bon exemple. Elle n'appartient pas à la page de connexion : après une connexion, on la trouve sur toutes les pages. En la mettant dans `BasePage`, `aller_au_back_office()` est disponible depuis n'importe quelle page.

### Exercice 11 — `BasePage`

**Énoncé**

Créez `pages/base_page.py`, faites-en hériter `LoginPage`, et réécrivez les deux autres tests de connexion.

**Règles / étapes**

1. Dans `BasePage` : le constructeur, `attendre`, `trouver`, `cliquer`, `saisir`, `texte`, `champ`, les locators `LIEN_BACK_OFFICE`, `DECONNEXION` et `TITRE`, et les méthodes `aller_au_back_office()`, `a_le_lien_back_office()`, `titre()`.
2. Retirez de `LoginPage` tout ce qui est maintenant dans `BasePage`. `LoginPage` garde ses locators de formulaire, `ouvrir`, `soumettre`, `se_connecter` et `message_erreur`.
3. Relancez le test du mauvais mot de passe : il ne doit pas avoir changé.
4. Réécrivez `test_organisateur_accede_au_back_office` et `test_client_est_redirige_hors_du_back_office`.

**Contraintes**

- `BasePage` ne contient rien qui soit propre à la page de connexion ;
- `a_le_lien_back_office()` ne fait pas d'attente : une vérification d'absence ne peut pas attendre. C'est au test de l'appeler au bon moment ;
- le test de redirection peut attendre sa redirection avec `page.attendre(lambda d: ...)` : c'est un résultat propre à ce test.

<details>
<summary>Indice 1</summary>

`aller_au_back_office` enchaîne trois choses déjà vues à l'exercice 5 : cliquer sur le lien, attendre l'URL, attendre le titre.

</details>

<details>
<summary>Indice 2</summary>

Sur macOS, la saisie robuste utilise `Keys.COMMAND`. Une constante en haut de `base_page.py` règle les deux cas :

```python
import sys

TOUT_SELECTIONNER = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
```

</details>

---

## 10. `PromosPage`

### 10.1 Une page qui lit et qui agit

`PromosPage` regroupe tout ce que `test_promos.py` sait de la page des codes promo.

| Ce que le test faisait | Méthode de `PromosPage` | Renvoie |
|---|---|---|
| ouvrir `/admin/promos` et attendre les codes | `ouvrir()` | `self` |
| lire la colonne des codes | `codes()` | une liste de textes |
| lire les cellules d'une ligne | `cellules(code)` | une liste de textes |
| lire le badge d'une ligne | `statut(code)` | un texte |
| compter les boutons « Desactiver » d'une ligne | `nombre_de_boutons_desactiver(code)` | un nombre |
| remplir le formulaire, cliquer, attendre la ligne | `creer(code, reduction, usages_max)` | `self` |
| cliquer sur « Desactiver », attendre `inactif` | `desactiver(code)` | `self` |

Le locator d'une ligne dépend du code : c'est une méthode qui le construit, et non un attribut.

```python
def ligne(self, code):
    """Renvoie le locator de la ligne d'un code."""
    return By.XPATH, f"//tr[td[normalize-space()='{code}']]"
```

`champ(libelle)`, hérité de `BasePage`, donne les locators des trois champs du formulaire : `self.champ("Reduction (%)")`.

### Exercice 12 — `PromosPage`

**Énoncé**

Créez `pages/promos_page.py` et réécrivez `tests/test_promos.py` avec `LoginPage` et `PromosPage`.

**Règles / étapes**

1. Écrivez la classe : ses deux locators (`CELLULES_CODE`, `BOUTON_CREER`), `ligne(code)` et les sept méthodes du tableau.
2. Dans les tests, la connexion se fait avec `LoginPage(driver).ouvrir().se_connecter(...)`.
3. La fonction locale `ouvrir_codes_promo` et la fonction `saisir` disparaissent du fichier de tests.
4. Lancez les tests.

**Contraintes**

- aucun test du fichier ne contient de locator ni d'attente ;
- les tests vérifient exactement les mêmes choses qu'avant.

<details>
<summary>Indice</summary>

`creer` reçoit des nombres. `saisir` tape du texte : convertissez avec `str(reduction)`.

</details>

---

## 11. La fixture `orga_driver`

### 11.1 Une fixture qui en utilise une autre

Tous les tests de codes promo commencent par la connexion de l'organisateur. C'est une préparation, pas l'objet du test : sa place est dans une fixture.

Une fixture peut demander une autre fixture. Ajoutez à `conftest.py` :

```python
import config
from pages.login_page import LoginPage


@pytest.fixture
def orga_driver(driver):
    """Navigateur avec une session organisateur ouverte."""
    LoginPage(driver).ouvrir().se_connecter(config.ORGA_EMAIL, config.ORGA_PASSWORD)
    return driver
```

- Un test qui demande `orga_driver` reçoit un navigateur créé par `driver`, puis connecté.
- `driver` reste responsable de la fermeture de Chrome. `orga_driver` n'a rien à ranger : `return` suffit.
- La fixture renvoie le navigateur, pas une page : chaque test construit la page dont il a besoin.

Le test des codes de démonstration devient :

```python
def test_codes_de_demonstration_listes(orga_driver):
    codes = PromosPage(orga_driver).ouvrir().codes()

    assert "WELCOME10" in codes
    assert "VIP25" in codes
    assert "EXPIRED" in codes
```

### Exercice 13 — `orga_driver`

1. Ajoutez la fixture `orga_driver` à `conftest.py`.
2. Dans `tests/test_promos.py`, remplacez `driver` par `orga_driver` et supprimez les connexions.
3. Lancez **toute** la suite, deux fois de suite. Elle doit rester entièrement verte.

---

## 12. Un scénario autonome

L'intérêt d'une architecture se mesure au moment d'ajouter quelque chose. Un nouveau scénario ne devrait demander que deux sortes de code : des méthodes dans les pages, et un test qui les utilise.

### Exercice 14 — Un nouveau scénario

**Énoncé**

Choisissez un ou plusieurs scénarios et ajoutez-les à la suite.

- **A. Un code existant est refusé.** Tenter de créer `WELCOME10` affiche le message `Code already exists`, et le tableau ne contient toujours qu'une ligne `WELCOME10`.
- **B. Un code saisi en minuscules est mis en majuscules.** Taper `sel-test` dans le champ `Code` affiche `SEL-TEST`, sans même envoyer le formulaire.
- **C. Le lien « Codes promo » du tableau de bord.** Depuis le tableau de bord (`/admin`), le lien « Codes promo » ouvre la page des codes promo. Ce scénario demande une nouvelle page, `DashboardPage`.
- **D. Les métriques du tableau de bord.** Le nombre d'événements publiés (`Publies`) ne dépasse pas le nombre total d'événements (`Evenements`).

**Règles / étapes**

1. Écrivez d'abord le test, comme si les méthodes existaient. Relisez-le : il doit décrire le scénario.
2. Lancez-le : il échoue sur une méthode manquante (`AttributeError`).
3. Ajoutez les méthodes nécessaires aux pages.
4. Relancez toute la suite.

**Contraintes**

- les tests n'utilisent que des méthodes de pages et des fixtures ;
- une page ne contient aucune assertion ;
- un test ne laisse aucun code actif derrière lui.

<details>
<summary>Indice pour A</summary>

`creer` attend la ligne du code. Pour `WELCOME10`, cette ligne existe déjà : l'attente réussirait immédiatement, sans prouver que le formulaire a été traité. Séparez `creer` en deux méthodes, `remplir(...)` et `envoyer()`, puis attendez le message d'erreur. Le message d'erreur a la même structure sur toutes les pages : `message_erreur()` peut monter dans `BasePage`.

</details>

<details>
<summary>Indice pour B</summary>

La valeur d'un champ se lit avec `get_attribute("value")`. Une méthode `valeur_du_champ(libelle)` dans `PromosPage` suffit.

</details>

<details>
<summary>Indice pour C</summary>

Une action qui mène à une autre page **renvoie un objet de la nouvelle page**, après avoir attendu qu'elle soit prête :

```python
def ouvrir_codes_promo(self):
    self.cliquer(self.LIEN_CODES_PROMO)
    page = PromosPage(self.driver)
    page.trouver(page.CELLULES_CODE)
    return page
```

Le lien contient une icône avant son texte : utilisez `normalize-space()`.

</details>

<details>
<summary>Indice pour D</summary>

Le libellé et la valeur d'une métrique sont deux `div` voisins, de classes `m-label` et `m-value`. Juste après l'ouverture de la page, la valeur affiche un tiret (`-`) le temps que les données arrivent : attendre que l'élément soit visible ne suffit pas. Il faut attendre que son texte soit différent de `-`, avec une `lambda`.

</details>

---

## 13. La boîte à outils

Votre suite EventFlow est terminée. Sur un autre projet, vous rencontrerez vite des situations qu'EventFlow ne présente pas : une liste déroulante, une alerte JavaScript, un cadre, un nouvel onglet, un menu qui n'apparaît qu'au survol. Ce chapitre les traite une par une.

Il commence par un ajout à votre `conftest.py`, utile dans tous les projets : une capture d'écran à chaque échec.

Le chapitre ne dépend pas des Page Objects : les tests utilisent seulement la fixture `driver` et `config.py`.

### 13.1 Une capture d'écran à chaque échec

Quand un test échoue sur un serveur d'intégration continue, personne n'a vu l'écran. Le message d'erreur dit **où** le test s'est arrêté ; une capture montre **ce qu'affichait** la page à ce moment : un message inattendu, une page de connexion, une page blanche. En entreprise, c'est le premier réflexe.

Selenium sait enregistrer une capture :

```python
driver.save_screenshot("captures/accueil.png")       # toute la fenêtre
element.screenshot("captures/formulaire.png")         # un seul élément
```

Il reste à le faire **automatiquement**, à chaque échec, sans toucher aux tests. C'est le rôle d'un **hook** pytest : une fonction au nom imposé, que pytest appelle lui-même à certains moments. Ajoutez à `conftest.py` l'import `re` et le hook suivant :

```python
import re


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """Enregistre une capture d'écran quand un test échoue."""
    rapport = yield
    if rapport.when == "call" and rapport.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            dossier = item.config.rootpath / "captures"
            dossier.mkdir(exist_ok=True)
            fichier = dossier / (re.sub(r"[^\w.-]", "_", item.name) + ".png")
            driver.save_screenshot(str(fichier))
            rapport.sections.append(("Capture d'écran", str(fichier)))
    return rapport
```

Vous n'avez pas à savoir écrire un hook ; il faut comprendre ce que fait celui-ci.

- pytest appelle `pytest_runtest_makereport` trois fois par test, pour fabriquer le rapport de chaque étape : la préparation des fixtures (`setup`), le test lui-même (`call`) et le rangement (`teardown`).
- `wrapper=True` et `yield` : pytest fabrique le rapport pendant le `yield`. Le code qui suit le reçoit dans `rapport`, peut le compléter, et doit le renvoyer.
- `rapport.when` indique l'étape, `rapport.failed` un échec. On ne capture que pour l'étape `call`, celle du test lui-même : au `teardown`, Chrome est déjà fermé.
- `item` représente le test. `item.funcargs` contient ses fixtures, y compris `driver` quand le test demande `orga_driver`.
- Le nom du test devient le nom du fichier. Un test paramétré s'appelle par exemple `test_statut_des_codes_de_demonstration[code_valide]` : `re.sub` remplace les caractères gênants dans un nom de fichier.
- `item.config.rootpath` est le dossier du projet : les captures vont dans `captures/`, d'où que vous lanciez pytest.
- `rapport.sections.append(...)` ajoute le chemin de la capture au rapport d'échec affiché dans le terminal.

Les captures ne doivent pas être enregistrées dans Git : si le projet est un dépôt, ajoutez une ligne `captures/` au fichier `.gitignore`.

### Exercice 15 — La capture en cas d'échec

**Énoncé**

Ajoutez le hook à votre `conftest.py` et vérifiez qu'il fonctionne.

**Règles / étapes**

1. Ajoutez le hook et l'import `re`.
2. Dans `test_page_de_connexion_s_ouvre`, remplacez le titre attendu par une valeur fausse. Lancez le test, retrouvez la section « Capture d'écran » dans le rapport, ouvrez l'image.
3. Faites de même avec un test de `test_promos.py` : changez le statut attendu de `WELCOME10`. Que montre la capture ?
4. Remettez les deux tests en état et relancez toute la suite : aucune capture ne doit être créée.

**Question** : la fixture `driver` ferme Chrome après le test. Pourquoi la capture est-elle quand même possible quand le test échoue ?

### 13.2 Un site d'entraînement

Les exercices qui suivent utilisent [the-internet](https://the-internet.herokuapp.com), un site conçu pour s'entraîner à l'automatisation : chaque page présente une difficulté. Il est en anglais et, contrairement à EventFlow, ses éléments ont souvent un `id` : on les trouve avec `By.ID`.

Ajoutez son adresse à `config.py` :

```python
# Site d'entraînement pour la boîte à outils
INTERNET_URL = os.getenv("INTERNET_URL", "https://the-internet.herokuapp.com").rstrip("/")
```

Créez `tests/test_outils.py`, avec une petite fonction qui ouvre une page du site et renvoie une attente prête à l'emploi :

```python
from selenium.webdriver.support.ui import WebDriverWait

import config


def ouvrir(driver, chemin):
    driver.get(config.INTERNET_URL + chemin)
    return WebDriverWait(driver, 10)
```

```python
wait = ouvrir(driver, "/dropdown")
```

### 13.3 Les listes déroulantes

Une liste déroulante HTML est un élément `<select>` qui contient des `<option>`. Selenium fournit la classe `Select` pour la manipuler :

```python
from selenium.webdriver.support.ui import Select

liste = Select(driver.find_element(By.ID, "dropdown"))

liste.select_by_visible_text("Option 2")    # par le texte affiché
liste.select_by_value("1")                  # par l'attribut value
liste.select_by_index(1)                    # par la position, à partir de 0

liste.first_selected_option.text            # l'option choisie
[option.text for option in liste.options]   # toutes les options
```

Préférez `select_by_visible_text` : c'est ce que voit l'utilisateur. `Select` ne fonctionne que sur un vrai `<select>`. Beaucoup de sites construisent leurs listes avec des `div` : on les traite alors comme n'importe quel élément, en cliquant pour ouvrir la liste puis sur l'option voulue.

### Exercice 16 — La liste déroulante

**Énoncé**

Sur la page `/dropdown`, vérifiez le contenu de la liste, puis choisissez une option par son texte et une autre par sa valeur.

**Règles / étapes**

1. Attendez la liste, enveloppez-la dans un `Select`.
2. Vérifiez la liste des textes de toutes les options.
3. Choisissez `Option 2` par son texte, vérifiez l'option sélectionnée.
4. Choisissez l'option de valeur `1`, vérifiez l'option sélectionnée.

**Contraintes**

- un seul test ;
- l'option sélectionnée est lue avec `first_selected_option`.

### 13.4 Les alertes JavaScript

`alert()`, `confirm()` et `prompt()` ouvrent une boîte de dialogue du navigateur. Elle ne fait pas partie de la page : on ne la trouve pas avec `find_element`. Selenium y accède par `driver.switch_to.alert`, après avoir attendu son ouverture :

```python
alerte = wait.until(EC.alert_is_present())    # renvoie l'alerte

alerte.text                                  # le message
alerte.accept()                              # bouton OK
alerte.dismiss()                             # bouton Annuler
alerte.send_keys("texte")                    # saisie, pour un prompt()
```

Une fois l'alerte ouverte, on peut aussi l'obtenir avec `driver.switch_to.alert`.

Tant qu'une alerte est ouverte, la page ne répond plus. Si le test essaie de lire la page sans avoir traité l'alerte, Selenium lève une `UnexpectedAlertPresentException`, et Chrome ferme l'alerte de lui-même : le test continue alors dans un état qui n'est pas celui que vous croyez.

### Exercice 17 — Les alertes

**Énoncé**

La page `/javascript_alerts` a trois boutons. Le paragraphe `id="result"` affiche ce que l'utilisateur a fait. Écrivez trois tests :

1. « Click for JS Alert » : le message de l'alerte est `I am a JS Alert` ; après OK, le résultat est `You successfully clicked an alert`.
2. « Click for JS Confirm » : après Annuler, le résultat est `You clicked: Cancel`.
3. « Click for JS Prompt » : après la saisie de `Selenium` et OK, le résultat est `You entered: Selenium`.

**Contraintes**

- chaque test attend l'alerte avec `EC.alert_is_present()` ;
- les boutons sont trouvés par leur texte.

### 13.5 Les cadres et les onglets

**Les cadres.** Un `<iframe>` ou un `<frame>` affiche une autre page à l'intérieur de la page. Selenium ne cherche que dans le document où il se trouve : un élément d'un cadre est introuvable tant qu'on n'est pas entré dans ce cadre.

```python
driver.switch_to.frame("frame-top")        # par son nom ou son id, ou par l'élément
driver.switch_to.parent_frame()            # remonter d'un niveau
driver.switch_to.default_content()         # revenir à la page principale
```

Un cadre se charge comme une page : on attend qu'il soit disponible, et la condition y entre en même temps :

```python
wait.until(EC.frame_to_be_available_and_switch_to_it("frame-top"))
```

**Les onglets et fenêtres.** Un lien `target="_blank"` ouvre un nouvel onglet, mais Selenium **reste** sur l'onglet de départ. Chaque onglet a un identifiant :

```python
depart = driver.current_window_handle        # l'onglet actuel
wait.until(EC.number_of_windows_to_be(2))    # attendre l'ouverture
driver.window_handles                        # tous les onglets ouverts
driver.switch_to.window(identifiant)         # passer sur un onglet
driver.close()                               # fermer l'onglet actuel (quit() ferme tout)
```

Après `close()`, Selenium ne se replace pas tout seul : il faut repasser sur l'onglet de départ avec `switch_to.window(depart)`.

### Exercice 18 — Cadres et onglets

**Énoncé**

Deux tests :

1. La page `/nested_frames` est découpée en cadres : `frame-top`, qui contient lui-même `frame-left`, `frame-middle` et `frame-right`, et `frame-bottom`. Le cadre du milieu affiche `MIDDLE`, celui du bas `BOTTOM`. Vérifiez ces deux textes.
2. Sur la page `/windows`, le lien « Click Here » ouvre un nouvel onglet. Vérifiez que son titre `h3` est `New Window`, fermez-le, puis vérifiez que l'onglet de départ a pour titre `The Internet`.

**Contraintes**

- entrées dans les cadres avec `frame_to_be_available_and_switch_to_it` ;
- le nouvel onglet est identifié comme celui qui n'est pas l'onglet de départ, pas par sa position dans `window_handles`.

<details>
<summary>Indice</summary>

Pour passer de `frame-middle` à `frame-bottom`, il faut d'abord revenir à la page principale : `frame-bottom` n'est pas à l'intérieur de `frame-top`.

</details>

### 13.6 Attendre la fin d'un chargement

Deux conditions du chapitre 4 n'ont pas encore servi.

- `presence_of_element_located` est vraie dès que l'élément existe dans le HTML, **même caché**. Le `.text` d'un élément caché est vide, et cliquer dessus échoue. Elle sert à compter ou à lire un attribut, rarement plus.
- `invisibility_of_element_located` est vraie quand l'élément est caché **ou absent**. Elle sert à attendre la disparition d'un indicateur de chargement (« Loading... », une roue qui tourne).

Le piège : juste après le clic qui lance le chargement, l'indicateur n'est peut-être pas encore apparu. Il est absent, donc `invisibility_of_element_located` est déjà vraie, et le test continue trop tôt. On attend d'abord son apparition, puis sa disparition.

### Exercice 19 — Le chargement

**Énoncé**

Sur la page `/dynamic_loading/1`, le bouton « Start » affiche « Loading... » pendant quelques secondes, puis le message `Hello World!`. Ce message est dans la page depuis le début, mais caché.

**Règles / étapes**

1. Ouvrez la page, attendez le bouton.
2. Avant de cliquer, trouvez le message (`#finish h4`) avec `presence_of_element_located` et vérifiez que son texte est vide.
3. Cliquez sur « Start ».
4. Attendez l'apparition, puis la disparition de l'indicateur (`id="loading"`).
5. Vérifiez le message.

**Question** : supprimez l'étape « attendre l'apparition » et relancez. Le test passe-t-il ? Pourquoi faut-il quand même garder cette étape ?

### 13.7 Les exceptions à reconnaître

Les exceptions de Selenium sont dans `selenium.common.exceptions`. Savoir les reconnaître fait gagner beaucoup de temps.

| Exception | Ce qu'elle veut dire | Que faire |
|---|---|---|
| `NoSuchElementException` | aucun élément ne correspond, à cet instant | attendre l'élément, vérifier le locator dans les DevTools, vérifier qu'il n'est pas dans un cadre |
| `TimeoutException` | la condition attendue n'est jamais devenue vraie | lire le locator et la condition : accent, faute de frappe, élément jamais affiché |
| `StaleElementReferenceException` | l'élément a été retiré ou reconstruit depuis qu'on l'a trouvé | le chercher de nouveau au moment de s'en servir (chapitre 6.4) |
| `ElementClickInterceptedException` | un autre élément est au-dessus et recevrait le clic : bandeau de cookies, fenêtre modale, en-tête fixe | fermer ou attendre la disparition de ce qui gêne ; faire défiler l'élément au centre de l'écran |
| `ElementNotInteractableException` | l'élément existe mais on ne peut pas agir dessus : caché, de taille nulle, désactivé | attendre qu'il soit visible ou cliquable ; faire d'abord l'action qui l'affiche (un survol, l'ouverture d'un menu) |
| `UnexpectedAlertPresentException` | une alerte est ouverte | la traiter (chapitre 13.4) |

**La mauvaise réponse** à toutes ces exceptions : les attraper avec `try` / `except` pour que le test passe. Elles signalent soit un test mal synchronisé, soit un vrai problème de l'application.

### 13.8 La souris et le JavaScript

**La souris.** Survol, double-clic, clic droit et glisser-déposer passent par `ActionChains`, qui enchaîne des gestes puis les exécute avec `perform()` :

```python
from selenium.webdriver.common.action_chains import ActionChains

ActionChains(driver).move_to_element(element).perform()          # survol
ActionChains(driver).double_click(element).perform()
ActionChains(driver).context_click(element).perform()            # clic droit
ActionChains(driver).drag_and_drop(source, cible).perform()
```

Sans `perform()`, rien ne se passe.

**Le JavaScript.** `execute_script` exécute du JavaScript dans la page. Les éléments passés en arguments sont disponibles dans `arguments[0]`, `arguments[1]`... Deux usages sont courants :

```python
# faire défiler la page jusqu'à un élément, placé au centre de l'écran
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

# cliquer en JavaScript : dernier recours
driver.execute_script("arguments[0].click();", element)
```

Le défilement est sans risque : il évite une partie des `ElementClickInterceptedException`, quand un en-tête fixe recouvre l'élément.

Le clic JavaScript, lui, ne fait aucune vérification : il clique sur un élément caché, recouvert ou désactivé, ce qu'aucun utilisateur ne pourrait faire. Un test qui clique ainsi peut passer alors que l'application est inutilisable. On ne s'en sert qu'après avoir compris pourquoi le clic normal échoue, et quand ce n'est pas le comportement testé.

### Exercice 20 — La souris

**Énoncé**

Deux tests :

1. La page `/hovers` montre trois avatars (`div.figure`). Survoler le deuxième affiche sa légende, `name: user2`. Vérifiez-le.
2. Sur la page `/context_menu`, un clic droit dans la zone `id="hot-spot"` ouvre une alerte. Vérifiez son message, `You selected a context menu`, et fermez-la.

**Contraintes**

- le survol et le clic droit passent par `ActionChains` ;
- la légende est attendue visible avant d'être lue.

**Bonus 1.** Sur la page `/drag_and_drop`, déplacez le bloc `A` (`id="column-a"`) sur le bloc `B`. Les deux blocs échangent leur contenu : le titre `header` du bloc de gauche devient `B`.

**Bonus 2.** Sur la page `/hovers`, sans survol, cliquez sur le lien « View profile » du premier avatar (`href` égal à `/users/1`). Quelle exception obtenez-vous, et pourquoi ? Cliquez ensuite sur le même lien avec `execute_script`. Que prouve un test qui passe de cette façon ?

---

## Aide-mémoire

### Le projet

| Fichier | Contenu |
|---|---|
| `requirements.txt` | `selenium`, `pytest` |
| `pytest.ini` | `testpaths = tests`, `pythonpath = .` |
| `config.py` | `BASE_URL`, `INTERNET_URL` et les comptes, lus dans l'environnement |
| `conftest.py` | fixtures `driver` et `orga_driver`, hook de capture d'écran |
| `pages/base_page.py` | actions élémentaires, barre de navigation, titre |
| `pages/login_page.py` | formulaire de connexion |
| `pages/promos_page.py` | tableau et formulaire des codes promo |

### Locators

```python
(By.CSS_SELECTOR, "input[type=email]")
(By.CSS_SELECTOR, "table.table tbody td.mono")
(By.XPATH, "//button[normalize-space()='Se connecter']")
(By.XPATH, "//label[normalize-space()='Code']/following-sibling::input")
(By.XPATH, "//tr[td[normalize-space()='WELCOME10']]")
(By.PARTIAL_LINK_TEXT, "Back-office")
```

### Attentes

```python
wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located(LOCATOR))        # pour lire ou remplir
wait.until(EC.element_to_be_clickable(LOCATOR)).click()       # pour cliquer
wait.until(EC.url_contains("/admin"))                         # après une navigation
wait.until(EC.text_to_be_present_in_element(LOCATOR, "inactif"))
wait.until(lambda d: not d.current_url.endswith("/admin"))
wait.until(EC.visibility_of_element_located(CHARGEMENT))       # apparition...
wait.until(EC.invisibility_of_element_located(CHARGEMENT))     # ...puis disparition
wait.until(EC.alert_is_present())                             # renvoie l'alerte
wait.until(EC.frame_to_be_available_and_switch_to_it("nom"))  # entre dans le cadre
wait.until(EC.number_of_windows_to_be(2))                     # un onglet s'est ouvert
```

### Page Objects

- Une classe par page, qui hérite de `BasePage`.
- Locators en attributs de classe, en majuscules.
- Une action attend ce qu'il faut et renvoie `self` ; une lecture renvoie une valeur.
- Aucune assertion dans une page ; aucun locator ni attente dans un test.

### Erreurs fréquentes

- Environnement virtuel non activé : `No module named 'selenium'`.
- `pytest.ini` absent ou sans `pythonpath = .` : `No module named 'config'` ou `'pages'`.
- EventFlow non démarré : `net::ERR_CONNECTION_REFUSED`.
- Lire un message juste après un clic, sans attente : `NoSuchElementException`.
- `time.sleep` à la place d'une attente explicite.
- `send_keys` sur un champ prérempli sans le vider, ou `clear()` seul sur un champ React.
- `//` au lieu de `.//` dans une recherche partant d'une ligne.
- Attendre une ligne du tableau alors qu'il affiche « Aucun code promo. ».
- Un code promo écrit en dur : le test échoue à la relance.
- Des accents dans un locator alors que l'interface n'en a pas.
- Une méthode d'action sans `return self` : `'NoneType' object has no attribute ...` à l'appel suivant.
- Oublier `self` dans la définition d'une méthode : `takes 1 positional argument but 2 were given`.
- Une assertion dans une page.
- Chercher un élément d'un cadre sans être entré dans le cadre : `NoSuchElementException`.
- Cliquer sur un lien `target="_blank"` et chercher dans le nouvel onglet sans `switch_to.window`.
- Oublier `perform()` après une `ActionChains`.
- Attendre la disparition d'un indicateur de chargement sans avoir attendu son apparition.
- Un clic JavaScript pour contourner une erreur qu'on n'a pas comprise.

---

## Annexe — Référence Selenium

Cette annexe ne résume pas le cours : c'est une référence pour vos prochains projets. Elle reprend les commandes du support et ajoute celles qu'EventFlow ne demande pas.

### Imports

```python
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
```

### Stratégies de recherche

| Stratégie | Exemple | Remarque |
|---|---|---|
| `By.ID` | `(By.ID, "dropdown")` | la plus stable, quand l'application pose des `id` |
| `By.NAME` | `(By.NAME, "email")` | fréquent dans les formulaires |
| `By.CSS_SELECTOR` | `(By.CSS_SELECTOR, "form button.btn-primary")` | le choix par défaut |
| `By.XPATH` | `(By.XPATH, "//button[normalize-space()='Creer']")` | pour un texte, un label, une ligne |
| `By.LINK_TEXT` | `(By.LINK_TEXT, "Click Here")` | texte exact d'un lien |
| `By.PARTIAL_LINK_TEXT` | `(By.PARTIAL_LINK_TEXT, "Back-office")` | partie du texte d'un lien |
| `By.CLASS_NAME` | `(By.CLASS_NAME, "badge")` | une seule classe, sans point |
| `By.TAG_NAME` | `(By.TAG_NAME, "td")` | surtout à l'intérieur d'un élément |

Si l'application a des attributs prévus pour les tests (`data-testid`, `data-test`), utilisez-les en priorité : `(By.CSS_SELECTOR, "[data-testid=submit]")`.

### CSS

| Sélecteur | Sélectionne |
|---|---|
| `input[id^='file']` | attribut qui **commence** par la valeur |
| `input[id$='submit']` | attribut qui **finit** par la valeur |
| `a[href*='elementalselenium']` | attribut qui **contient** la valeur |
| `tr:nth-child(2)` | élément qui est le deuxième enfant de son parent |
| `ul > li` | enfant direct (et non descendant quelconque) |

### XPath

| Expression | Sélectionne |
|---|---|
| `//button[normalize-space()='Creer']` | texte exact, espaces de bord ignorés |
| `//h3[contains(text(), 'Uploader')]` | texte qui contient une valeur |
| `//div[contains(@class, 'badge')]` | classe parmi plusieurs |
| `//label[normalize-space()='Code']/following-sibling::input` | élément voisin, placé après |
| `//input[@id='file-submit']/ancestor::form` | ancêtre (parent, grand-parent...) |
| `//tr[td[normalize-space()='WELCOME10']]` | élément qui contient un élément donné |
| `.//button` | recherche à partir de l'élément courant |

### Navigateur et navigation

```python
driver.get(url)
driver.back()
driver.forward()
driver.refresh()
driver.current_url
driver.title
driver.save_screenshot("captures/page.png")
element.screenshot("captures/element.png")
```

### Éléments

```python
element.click()
element.clear()
element.send_keys("texte")
element.send_keys(Keys.ENTER)
element.text                       # texte affiché ("" si l'élément est caché)
element.get_attribute("value")     # valeur d'un champ, ou tout autre attribut
element.is_displayed()
element.is_enabled()
element.is_selected()              # case à cocher, bouton radio
```

### Envoyer un fichier

On n'ouvre pas la fenêtre de choix de fichier : on tape le **chemin absolu** du fichier dans le champ `input[type=file]`.

```python
driver.find_element(By.ID, "file-upload").send_keys(str(chemin.resolve()))
driver.find_element(By.ID, "file-submit").click()
```

La fixture pytest `tmp_path` fournit un dossier temporaire pour créer le fichier pendant le test.

### Listes, alertes, cadres, onglets

```python
Select(element).select_by_visible_text("Option 2")
Select(element).first_selected_option.text

alerte = wait.until(EC.alert_is_present())
alerte.text; alerte.accept(); alerte.dismiss(); alerte.send_keys("texte")

driver.switch_to.frame("nom")          # ou un élément <iframe>
driver.switch_to.parent_frame()
driver.switch_to.default_content()

depart = driver.current_window_handle
driver.window_handles
driver.switch_to.window(identifiant)
driver.switch_to.new_window("tab")     # ouvre un onglet vide et s'y place
driver.close()
```

### Souris et JavaScript

```python
ActionChains(driver).move_to_element(element).perform()
ActionChains(driver).double_click(element).perform()
ActionChains(driver).context_click(element).perform()
ActionChains(driver).drag_and_drop(source, cible).perform()

driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
driver.execute_script("arguments[0].click();", element)      # dernier recours
```

### Cookies

```python
driver.get_cookies()
driver.get_cookie("nom")
driver.add_cookie({"name": "nom", "value": "valeur"})    # sur la page du site concerné
driver.delete_all_cookies()
```

### Outils autour de pytest

| Outil | Installation | Utilisation |
|---|---|---|
| pytest-xdist : tests en parallèle | `pip install pytest-xdist` | `pytest -n 4` |
| pytest-html : rapport HTML | `pip install pytest-html` | `pytest --html=rapport.html --self-contained-html` |

Avec pytest-xdist, chaque test doit être indépendant des autres : ses propres données, son propre navigateur. C'est déjà le cas de votre suite EventFlow.

### Selenium Grid

Selenium Grid fait tourner les navigateurs sur d'autres machines : plusieurs navigateurs, plusieurs systèmes, en parallèle. Le test ne change pas ; seule la création du `driver` change :

```python
drv = webdriver.Remote(command_executor="http://grille:4444", options=webdriver.ChromeOptions())
```

Les services en ligne de navigateurs (Sauce Labs, BrowserStack...) fonctionnent de la même façon.

<!-- xpath -->
| Syntaxe | Signification |
|---------|---------------|
| `//` | Chercher partout dans le document |
| `/` | Enfant direct |
| `@` | Cibler un attribut |
| `*` | N'importe quelle balise |
| `.` | Élément courant |
| `..` | Élément parent |
| `[ ]` | Ajouter une condition |
| `text()` | Cibler le texte |
| `contains()` | Chercher une correspondance partielle |
