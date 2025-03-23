# budget_buddy
# 💸 BudgetBuddy

**BudgetBuddy** is a modern, responsive, and feature-rich personal finance tracker built with Django and Bootstrap. It allows users to manage their income, expenses, budgets, savings goals, investments, and shared finances — all in one place!

---

## 🚀 Features

### 🔐 User Authentication
- Signup, login, logout
- Custom user model
- Profile and settings

### 💰 Income & Expense Tracking
- Manual logging
- Categorization and tagging
- Edit/delete transactions

### 🧾 Budget Management
- Set monthly spending limits
- Visual warnings for overspending

### 🐷 Goal-Based Savings
- Create and track savings goals
- Set deadlines and targets

### 📊 Financial Reports
- Charts for income vs expenses
- Monthly trends, summaries
- Exportable insights
  
### 👥 Shared Budgeting
- Create shared budgets
- Split expenses among members
- Group-based analytics

### 📈 Investment & Crypto Tracking
- Real-time stock/crypto prices via Yahoo Finance API
- Portfolio profit/loss calculations

---

## 🛠️ Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **API Integration**: Yahoo Finance (via `yfinance`)
- **Testing**: Django `TestCase` framework
- **Version Control**: Git

---

## 📦 Project Structure
budgetbuddy/ │ ├── authentication/ # User auth logic ├── transactions/ # Income and expense tracking ├── shared_budgeting/ # Expense sharing and group budgets ├── savings/ # Goal-based savings tracking ├── investments/ # Stock and crypto monitoring ├── reports/ # Financial charts and insights ├── dashboard/ # User dashboard and summary ├── templates/ # HTML templates ├── static/ # CSS/JS files └── manage.py

