# XPath — aide-mémoire Selenium

XPath permet de retrouver un élément HTML par sa balise, ses attributs, son texte ou sa position dans la page.

## Syntaxe de base

| XPath | Ce que ça cherche |
|---|---|
| `//button` | Tous les boutons de la page |
| `//input[@type='email']` | Un input dont le type est `email` |
| `//button[normalize-space()='Se connecter']` | Un bouton avec ce texte (espaces superflus ignorés) |
| `//button[contains(@class, 'primary')]` | Un bouton dont la classe contient `primary` |
| `//tr[td[normalize-space()='WELCOME10']]` | Une ligne contenant une cellule `WELCOME10` |
| `(//button)[1]` | Le premier bouton de la page |

### Les symboles

- `/` : enfant direct. `//form/button`
- `//` : descendant, peu importe la profondeur. `//form//button`
- `@` : attribut HTML. `//input[@placeholder='SUMMER20']`
- `[...]` : condition / filtre. `//input[@type='email']`
- `.` : élément actuel. `.//button` cherche dans l'élément courant.
- `..` : parent direct. `//label/..`
- `and`, `or` : combiner des conditions. `//input[@type='email' and @required]`

## Les axes XPath

Les axes servent à naviguer à partir d'un élément déjà trouvé.

| Axe | Utilité | Exemple |
|---|---|---|
| `parent::` | Parent direct | `//label/parent::div` |
| `ancestor::` | Parents à plusieurs niveaux | `//input/ancestor::form` |
| `child::` | Enfant direct | `//form/child::button` |
| `descendant::` | Tous les descendants | `//form/descendant::input` |
| `following-sibling::` | Éléments frères après | `//label[normalize-space()='Email']/following-sibling::input` |
| `preceding-sibling::` | Éléments frères avant | `//input/preceding-sibling::label` |
| `following::` | Éléments situés après dans le document | `//h2/following::button` |
| `preceding::` | Éléments situés avant dans le document | `//button/preceding::h2` |

Exemple EventFlow : retrouver le champ à partir de son label :

```xpath
//label[normalize-space()='Mot de passe']/following-sibling::input
```

## Dans Selenium

```python
from selenium.webdriver.common.by import By

bouton = driver.find_element(By.XPATH, "//button[normalize-space()='Se connecter']")
bouton.click()

# Chercher uniquement à l'intérieur d'une ligne déjà trouvée
ligne = driver.find_element(By.XPATH, "//tr[td[normalize-space()='WELCOME10']]")
boutons = ligne.find_elements(By.XPATH, ".//button")
```

- `find_element` : premier élément trouvé, erreur si aucun.
- `find_elements` : liste des éléments, vide si aucun.
- `//button` cherche dans toute la page ; `.//button` cherche dans l'élément courant.

## Tester et éviter les pièges

- Chrome DevTools → **Elements** → `Ctrl + F` → coller le XPath. Vérifier le nombre de résultats.
- Dans la console Chrome : `$x("//button[normalize-space()='Se connecter']")`. Attention : `$()` sert aux sélecteurs CSS, pas XPath.
- Privilégier un `id`, un attribut stable ou un sélecteur simple quand c'est possible.
- Éviter les chemins absolus comme `/html/body/div[2]/div[1]/button` : trop fragiles.
- Éviter de dépendre de `[1]`, `[2]`, etc. si les éléments risquent de bouger.
- Un bon locator doit viser **un seul élément** quand on veut interagir avec lui.
