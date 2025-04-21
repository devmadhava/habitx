# Habit_X

**Habit_X** is a flexible habit tracking application designed to help you build and maintain habits with ease. Track your habits daily or weekly, monitor your streaks, and gain insights into your consistency — all from the command line or an interactive TUI (Text-based User Interface).

---


## ⚙️ Requirements

- **Python 3.8+**
- Recommended: Use a virtual environment for managing dependencies.
- If you are running this in Windows, make sure **Python is added to your system's PATH/environment variables** so you can run `habit_x` from anywhere.

---

## 🚀 Features

- Track daily or weekly habits
- Automatically calculate current, longest, and average streaks (consistency)
- View most/least consistent habits
- Timezone-aware tracking. All data is stored in UTC but can be displayed in user selected Timezone
- Simple CLI and full-screen TUI for managing and visualizing habits
- Lightweight SQLite + Peewee ORM backend

---

## 📦 Installation

Make sure you have **Python 3.8+** or above installed.

1. **Install from a Build:**
- Download the latest **.whl** or **.tar.gz** file from the **dist/** folder (or GitHub Releases).
- Click and Run the **.whl** file or use the following command to install application from terminal


```bash
pip install habitx-0.1.0.tar
```

2. **Install from Source:**
```bash
git clone https://github.com/devmadhava/habitx.git
cd  habit_x
pip install .
```

---

## 🚀 Running Habit X

You can use habit_x in two ways:

1. ***In TUI Mode***: Just run either of these two commands
```bash
habit_x
```

or 

```bash
habit_x run
```

<br>

2. ***In CLI Mode***: Run specific commands directly:

```bash
habit_x <command> [options]
```

---

## 📁 Available Commands

### ➕ add

**Add a new habit.**

| Flag | Description                       | Example                                 |
|------|-----------------------------------|-----------------------------------------|
| -n   | Habit Name                        | Example: habitx -n "Running Daily"      |
| -d   | Description of the Habit          | Example: habitx -d "Run 10 KM everyday" |
| -f   | Habit Frequency (Daily or Weekly) | Example: habitx -f daily                |


Example: 
```bash 
habitx add -n Running -d "Lets Run 12 KM a day" -f DAILY
```


<br>

### ❌ delete

**Delete a habit by ID.**

| Flag | Description                                                        | Example                     |
|------|--------------------------------------------------------------------|-----------------------------|
| -i   | ID of the habit to delete. If not provided, user will be prompted. | Example: habitx delete -i 1 |

Example: 
```bash 
habitx delete -i 1
```


<br>

### ✏️ edit

**Edit a habit’s name and/or description.**

| Flag | Description                                                      | Example                                                             |
|------|------------------------------------------------------------------|---------------------------------------------------------------------|
| -i   | ID of the habit to edit. If not provided, user will be prompted. | Example: habitx edit -i 1                                           |
| -n   | The new name of the habit.                                       | Example: habitx edit -i 1 -n "Morning Jog"                          |
| -d   | The new description of the habit.                                | Example: habitx edit -i 1 -d "Jogging for 30 minutes every morning" |

Example: 
```bash 
habitx edit -i 1 -n "New Name" -d "New Description"
```


<br>

### ✅ mark

**Mark a habit as completed for today.**

| Flag | Description                                                                   | Example                   |
|------|-------------------------------------------------------------------------------|---------------------------|
| -i   | ID of the habit to mark as completed. If not provided, user will be prompted. | Example: habitx mark -i 2 |


Example: 
```bash 
habitx mark -i 1
```


<br>

### 🔄 unmark

**Unmark (undo) a completion for a habit.**

| Flag | Description                                                        | Example                     |
|------|--------------------------------------------------------------------|-----------------------------|
| -i   | ID of the habit to unmark. If not provided, user will be prompted. | Example: habitx unmark -i 2 |

Example: 
```bash 
habitx unmark -i 1"
```


<br>

### 📋 list

**List all habits with optional filters.**

| Flag | Description                                             | Example                       |
|------|---------------------------------------------------------|-------------------------------|
| -d   | Habit Creation Date                                     | Example: habitx -d 01.01.2020 |
| -c   | Date in which Habit was completed                       | Example: habitx -c 01.01.2020 |
| -f   | Habit Frequency (Daily or Weekly)                       | Example: habitx -f daily      |
| -streak | Indicates If user wants to fetch streaks data (Boolean) | Example habitx -streak |

Example: 
```bash 
habitx list -streak -d 01.01.2020 -f "DAILY" -c 02.02.2020
```


<br>

### 📈 streak

**Show streak statistics for a habit.**

| Flag | Description                                                                  | Example                     |
|------|------------------------------------------------------------------------------|-----------------------------|
| -i   | ID of the habit to view streaks for. If not provided, user will be prompted. | Example: habitx streak -i 1 |

Example: 
```bash 
habitx streak -i 1
```


<br>

### 📊 consistent

**Show most and least consistent habits.**

| Flag | Description                                                     | Example                    |
|------|-----------------------------------------------------------------|----------------------------|
| N/A  | No flags required. Displays consistency metrics for all habits. | Example: habitx consistent |

Example: 
```bash 
habitx consistent
```


<br>

### 👤 user

**Manage user preferences.**

| Flag | Description                                            | Example                                     |
|------|--------------------------------------------------------|---------------------------------------------|
| -e   | If True, prompts the user to edit their configuration. | Example: habitx user -e                     |
| -n   | The new username. If None, prompts the user.           | Example: habitx user -n "NewUsername"       |
| -tz  | The new timezone. If None, prompts the user.           | Example: habitx user -tz "America/New_York" |
| -c   | The new terminal color. If None, prompts the user.     | Example: habitx user -c "green"             |

Example: 
```bash 
habitx user -n "New Name" -c "Red" -tz "Europe/Berlin"
```


<br>

### 🧭 run

**Start the Text User Interface.**

Launch it with either

```bash 
habitx
```

or 
```bash 
habitx run
```

---

## 📁 Project Structure

```bash
habit_x/
├── habit_tracker/      # Main package
├── tests/              # Pytest test suite
├── dist/               # Contains .whl and .tar.gz builds
├── docs/               # Contains documentation for application
├── setup.py            # Installation script
└── README.md
```

---

## 🧪 Running Tests

To run the full test suite using pytest:
- Clone the Repository
- Install the requirements
- Run the following command
- 
```bash
pytest
```