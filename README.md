# [Square Wars][itch-io-page]

## Authors
<table border="0">
  <tr>
    <td>
      <a href="https://github.com/JiffyRob">
        <img alt="JiffyRob's profile picture" src="https://avatars.githubusercontent.com/u/101531330?v=4" width=50>
      </a>
    </td>
    <td>
      <a href="https://github.com/JiffyRob">
        JiffyRob
      </a>
    </td>
  </tr>
  <tr>
    <td>
      <a href="https://github.com/Matiiss">
        <img alt="Matiiss's profile picture" src="https://avatars.githubusercontent.com/u/83066658?v=4" width=50>
      </a>
    </td>
    <td>
      <a href="https://github.com/Matiiss">
        Matiiss
      </a>
    </td>
  </tr>
</table>

## Installation

### The easiest way is to go to the [itch.io page for this game][itch-io-page], download the correct zip for your OS, extract it, and have fun!
**itch.io page: [`jiffyrob.itch.io/square-wars`][itch-io-page]**

<br>

---

### However, if you wish to build and run from source:
#### 1. Create a virtual environment and activate it _(optional, recommended)_
```
python -m venv .venv
.venv/scripts/activate  # on Windows
source .venv/bin/activate  # on Unix systems
```

#### 2. Install the SquareWars package from the GitHub repository
```
pip install git+https://github.com/Matiiss/SquareWars
```

For development use
```
git clone https://github.com/Matiiss/SquareWars
cd SquareWars
pip install -e .[dev]
```

#### 3. Run the game
You can just type this in the terminal (while the environment you installed it in is active):
```
square-wars
```

Or run this from the root of the project:
```
python run.py
```

[itch-io-page]: https://jiffyrob.itch.io/square-wars "jiffyrob.itch.io/square-wars"
