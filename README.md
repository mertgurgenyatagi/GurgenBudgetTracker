# Gurgen Budget Tracker v1.0

A comprehensive personal finance management application built with Python and Tkinter, featuring advanced analytics, interactive visualizations, and automatic balance tracking.

## 🚀 Features

### 📊 **Dashboard**
- Real-time current balance display with color-coded indicators
- Quick overview of financial health
- Instant navigation to other sections

### 💰 **Transaction Management**
- Add income and expense transactions with custom labels and types
- Categorize transactions by predefined or custom labels
- Automatic data validation and error handling
- CSV-based data storage for reliability and portability

### 🏷️ **Labels & Types Management**
- Create and manage custom expense and income labels
- Organize labels into types for better categorization
- Seamless integration with transaction entry

### 📈 **Advanced Analytics**
- **General Flow Section**: Time-filtered totals and daily averages
- **Labels & Types Section**: Interactive analysis with 4 dropdown controls
  - Flow selection (Expenses/Incomes)
  - Time period filtering
  - Category view (By label/By type)
  - Display mode (Numerical/Interactive Charts)
- **Trend Analysis**: Page-wide line charts with gradient fills
  - Support for Expenses, Incomes, and Balance trends
  - Interactive hover tooltips
  - Smart positioning to prevent chart clipping

### 🎯 **Interactive Visualizations**
- **Bar Charts**: Hover-only tooltips with smart positioning
- **Pie Charts**: Interactive segments with detailed information
- **Line Charts**: Gradient-filled trend analysis with color coding
- **Responsive Design**: Adapts to window size changes

### 💾 **Data Management**
- **Automatic Backup System**: Hourly backups with timestamped folders
- **Daily Balance Tracking**: Automatic recording of daily balance history
- **CSV-based Storage**: Human-readable and easily portable data
- **Privacy Protection**: User data excluded from version control

## 🖥️ **System Requirements**

- Python 3.7 or higher
- Required Python packages:
  - `tkinter` (usually included with Python)
  - `ttkthemes`
  - `matplotlib`
  - `csv` (built-in)
  - `datetime` (built-in)

## 🔧 **Installation**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mertgurgenyatagi/GurgenBudgetTracker.git
   cd GurgenBudgetTracker
   ```

2. **Install required packages:**
   ```bash
   pip install ttkthemes matplotlib
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## 📁 **File Structure**

```
GurgenBudgetTracker/
├── main.py                          # Main application file
├── user_data/                       # Data storage directory
│   ├── transactions_database.csv    # Transaction records
│   ├── balance_database.csv         # Daily balance history
│   ├── expense_labels.csv           # Expense label definitions
│   └── income_labels.csv            # Income label definitions
├── backup_log.json                  # Backup tracking (auto-generated)
└── README.md                        # This file
```

## 🎨 **User Interface**

### **Window Layout**
- **Compact Design**: 700x500 pixel window for efficiency
- **Left Sidebar**: Navigation menu with 5 main sections
- **Main Area**: Dynamic content area with responsive layouts

### **Color Scheme**
- **Expenses**: Red (#dc3545) for expense-related data
- **Incomes**: Green (#28a745) for income-related data
- **Balance**: Blue (#007bff) for balance trends
- **UI Theme**: Modern "clam" theme with clean aesthetics

## 📊 **Analytics Features**

### **General Flow Analysis**
- Time period selection (Today, Last 7/30/365 days, All time)
- Total and average calculations
- Real-time balance computation

### **Labels & Types Analysis**
- **Four-dropdown interface:**
  1. **Flow**: Expenses/Incomes
  2. **Period**: Independent time filtering
  3. **Category**: By label or by type
  4. **View**: Numerical data or interactive charts
- **Dynamic content**: Updates automatically on selection changes

### **Trend Analysis**
- **Line charts** with gradient fills
- **Multi-data support**: Expenses, Incomes, and Balance tracking
- **Smart date handling**: Forward-filling for missing balance data
- **Interactive visualization**: Hover tooltips and responsive design

## 🔄 **Automatic Features**

### **Daily Balance Recording**
- Automatically records current balance as previous day's balance
- Runs on first app initialization each day
- Maintains historical balance database

### **Backup System**
- Hourly automatic backups
- Timestamped backup folders
- Preserves data integrity

### **Data Validation**
- Input validation for numerical fields
- Date format consistency
- Error handling and user feedback

## 🛠️ **Technical Details**

### **Architecture**
- **Object-oriented design** with modular page structure
- **Event-driven programming** for responsive UI updates
- **CSV-based data persistence** for simplicity and portability

### **Performance Optimizations**
- **Lazy loading** of chart data
- **Efficient memory management** for large datasets
- **Responsive UI updates** without blocking

### **Data Privacy**
- User data stored locally only
- No external data transmission
- Git-ignored user data for privacy protection

## 📋 **Usage Guide**

### **Adding Transactions**
1. Navigate to "Transactions" page
2. Select transaction type (Income/Expense)
3. Enter amount, choose label and type
4. Click "Add Transaction"

### **Managing Labels**
1. Go to "Labels & Types" page
2. Add new labels and assign types
3. Labels automatically appear in transaction dropdowns

### **Viewing Analytics**
1. Open "Analytics" page
2. Use "General Flow" for overview statistics
3. Explore "Labels & Types" with dropdown filters
4. Check "Trend Analysis" for visual trends

### **Balance Tracking**
- Balance automatically calculated from all transactions
- Daily balance recorded automatically
- View balance trends in Analytics → Trend Analysis → Balance

## 🚀 **Version History**

### **v1.0 (August 27, 2025)**
- Initial release with complete feature set
- Advanced analytics with interactive visualizations
- Automatic balance tracking system
- Responsive UI design optimized for 700x500 window
- Comprehensive backup and data management

## 🤝 **Contributing**

This is a personal finance application. While it's open source, it's designed for individual use. Feel free to fork and modify for your own needs.

## 📝 **License**

This project is open source. Feel free to use, modify, and distribute as needed.

## 👨‍💻 **Author**

**Mert Gürgen Yatağı**
- GitHub: [@mertgurgenyatagi](https://github.com/mertgurgenyatagi)

## 🔮 **Future Enhancements**

Potential future features could include:
- Data export functionality
- Advanced filtering options
- Budget planning tools
- Mobile app version
- Cloud synchronization options

---

**Gurgen Budget Tracker v1.0** - Personal Finance Management Made Simple 💰📊
