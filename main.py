import flet as ft
from datetime import datetime
import sqlite3

# إنشاء اتصال بقاعدة البيانات
conn = sqlite3.connect('penalty_system.db', check_same_thread=False)
cursor = conn.cursor()

# إنشاء جدول لتخزين السجلات إذا لم يكن موجودًا
cursor.execute('''
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    complaint_date TEXT,
    vehicle_number TEXT,
    driver_name TEXT,
    plate_number TEXT,
    description TEXT
)
''')
conn.commit()

class PenaltySystem:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Penalty Committee System"
        self.page.window_width = 400
        self.page.window_height = 600
        self.page.scroll = "auto"
        self.page.padding = 10

        # إنشاء الواجهة
        self.create_widgets()

    def create_widgets(self):
        # عنوان النظام
        title_label = ft.Text("Penalty Committee System", size=20, weight="bold", text_align="center")
        self.page.add(title_label)

        # قسم الإدخال
        self.category_dropdown = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("Taxis"),
                ft.dropdown.Option("Citizen Complaints on Taxis"),
                ft.dropdown.Option("Light Trucks"),
                ft.dropdown.Option("Heavy Trucks"),
                ft.dropdown.Option("Buses"),
            ],
            value="Taxis",
            width=300,
        )

        self.complaint_date_field = ft.TextField(
            label="Complaint Date",
            value=datetime.now().strftime("%Y-%m-%d"),
            width=300,
        )

        self.vehicle_number_field = ft.TextField(
            label="Vehicle Number",
            width=300,
        )

        self.driver_name_field = ft.TextField(
            label="Driver Name",
            width=300,
        )

        self.plate_number_field = ft.TextField(
            label="Plate Number",
            width=300,
        )

        self.description_field = ft.TextField(
            label="Description",
            width=300,
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        add_button = ft.ElevatedButton(
            text="Add Record",
            on_click=self.add_record,
            width=300,
        )

        input_section = ft.Column(
            controls=[
                self.category_dropdown,
                self.complaint_date_field,
                self.vehicle_number_field,
                self.driver_name_field,
                self.plate_number_field,
                self.description_field,
                add_button,
            ],
            spacing=10,
        )

        # قسم البحث
        self.search_field = ft.TextField(
            label="Search",
            width=300,
        )

        self.search_category_dropdown = ft.Dropdown(
            label="Category",
            options=[
                ft.dropdown.Option("All"),
                ft.dropdown.Option("Taxis"),
                ft.dropdown.Option("Citizen Complaints on Taxis"),
                ft.dropdown.Option("Light Trucks"),
                ft.dropdown.Option("Heavy Trucks"),
                ft.dropdown.Option("Buses"),
            ],
            value="All",
            width=300,
        )

        search_button = ft.ElevatedButton(
            text="Search",
            on_click=self.search_records,
            width=150,
        )

        show_all_button = ft.ElevatedButton(
            text="Show All",
            on_click=self.show_all_records,
            width=150,
        )

        search_section = ft.Column(
            controls=[
                self.search_field,
                self.search_category_dropdown,
                ft.Row(controls=[search_button, show_all_button], spacing=10),
            ],
            spacing=10,
        )

        # قسم عرض البيانات
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Category")),
                ft.DataColumn(ft.Text("Complaint Date")),
                ft.DataColumn(ft.Text("Vehicle Number")),
                ft.DataColumn(ft.Text("Driver Name")),
                ft.DataColumn(ft.Text("Plate Number")),
                ft.DataColumn(ft.Text("Description")),
            ],
            rows=[],
        )

        data_display_section = ft.Column(
            controls=[
                ft.Text("Records", size=16, weight="bold"),
                ft.Container(
                    content=self.data_table,
                    height=200,
                    width=380,
                    padding=10,
                    border=ft.border.all(1, ft.colors.GREY),
                ),
            ],
            spacing=10,
        )

        # أزرار التعديل والحذف
        edit_button = ft.ElevatedButton(
            text="Edit",
            on_click=self.edit_record,
            width=150,
        )

        delete_button = ft.ElevatedButton(
            text="Delete",
            on_click=self.delete_record,
            width=150,
        )

        button_section = ft.Row(
            controls=[edit_button, delete_button],
            spacing=10,
        )

        # تذييل الصفحة
        footer_label = ft.Text("Developed by @Hatice9423 | Version 1.0", size=12, text_align="center")

        # إضافة جميع الأقسام إلى الصفحة
        self.page.add(
            input_section,
            search_section,
            data_display_section,
            button_section,
            footer_label,
        )

        # تحميل السجلات عند فتح التطبيق
        self.show_all_records()

    def add_record(self, e):
        # الحصول على البيانات من الحقول
        category = self.category_dropdown.value
        complaint_date = self.complaint_date_field.value
        vehicle_number = self.vehicle_number_field.value
        driver_name = self.driver_name_field.value
        plate_number = self.plate_number_field.value
        description = self.description_field.value

        # التحقق من تعبئة جميع الحقول
        if not all([complaint_date, vehicle_number, driver_name, plate_number, description]):
            self.page.snack_bar = ft.SnackBar(ft.Text("Please fill all fields!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # إضافة السجل إلى قاعدة البيانات
        cursor.execute('''
        INSERT INTO records (category, complaint_date, vehicle_number, driver_name, plate_number, description)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (category, complaint_date, vehicle_number, driver_name, plate_number, description))
        conn.commit()

        # تحديث الجدول
        self.show_all_records()
        self.page.snack_bar = ft.SnackBar(ft.Text("Record added successfully!"))
        self.page.snack_bar.open = True
        self.page.update()

        # مسح الحقول
        self.clear_entries()

    def search_records(self, e):
        # الحصول على معايير البحث
        search_text = self.search_field.value.strip().lower()
        search_category = self.search_category_dropdown.value

        # البحث في قاعدة البيانات
        query = '''
        SELECT * FROM records
        WHERE (category = ? OR ? = 'All')
        AND (vehicle_number LIKE ? OR driver_name LIKE ? OR plate_number LIKE ? OR description LIKE ?)
        '''
        cursor.execute(query, (
            search_category, search_category,
            f"%{search_text}%", f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"
        ))
        filtered_records = cursor.fetchall()

        # تحديث الجدول
        self.update_table(filtered_records)

    def show_all_records(self, e=None):
        # جلب جميع السجلات من قاعدة البيانات
        cursor.execute("SELECT * FROM records")
        records = cursor.fetchall()

        # تحديث الجدول
        self.update_table(records)

    def update_table(self, records):
        # مسح البيانات القديمة
        self.data_table.rows.clear()

        # إضافة البيانات الجديدة
        for record in records:
            self.data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(record[1])),  # Category
                        ft.DataCell(ft.Text(record[2])),  # Complaint Date
                        ft.DataCell(ft.Text(record[3])),  # Vehicle Number
                        ft.DataCell(ft.Text(record[4])),  # Driver Name
                        ft.DataCell(ft.Text(record[5])),  # Plate Number
                        ft.DataCell(ft.Text(record[6])),  # Description
                    ]
                )
            )

        # تحديث الصفحة
        self.page.update()

    def edit_record(self, e):
        # الحصول على السجل المحدد
        selected_index = self.get_selected_index()
        if selected_index is None:
            self.page.snack_bar = ft.SnackBar(ft.Text("Please select a record to edit!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # جلب بيانات السجل المحدد
        record_id = self.data_table.rows[selected_index].cells[0].content.value
        cursor.execute("SELECT * FROM records WHERE id = ?", (record_id,))
        record = cursor.fetchone()

        # تعبئة الحقول ببيانات السجل المحدد
        self.category_dropdown.value = record[1]
        self.complaint_date_field.value = record[2]
        self.vehicle_number_field.value = record[3]
        self.driver_name_field.value = record[4]
        self.plate_number_field.value = record[5]
        self.description_field.value = record[6]

        # حذف السجل القديم
        self.delete_record()

    def delete_record(self, e=None):
        # الحصول على السجل المحدد
        selected_index = self.get_selected_index()
        if selected_index is None:
            self.page.snack_bar = ft.SnackBar(ft.Text("Please select a record to delete!"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # تأكيد الحذف
        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirm"),
            content=ft.Text("Are you sure you want to delete this record?"),
            actions=[
                ft.TextButton("Yes", on_click=lambda e: self.confirm_delete(selected_index)),
                ft.TextButton("No", on_click=lambda e: self.close_dialog()),
            ],
        )

        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    def confirm_delete(self, index):
        # حذف السجل من قاعدة البيانات
        record_id = self.data_table.rows[index].cells[0].content.value
        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        conn.commit()

        # تحديث الجدول
        self.show_all_records()
        self.page.snack_bar = ft.SnackBar(ft.Text("Record deleted successfully!"))
        self.page.snack_bar.open = True
        self.close_dialog()

    def close_dialog(self):
        self.page.dialog.open = False
        self.page.update()

    def get_selected_index(self):
        # الحصول على الفهرس المحدد
        for i, row in enumerate(self.data_table.rows):
            if row.selected:
                return i
        return None

    def clear_entries(self):
        # مسح جميع الحقول
        self.complaint_date_field.value = datetime.now().strftime("%Y-%m-%d")
        self.vehicle_number_field.value = ""
        self.driver_name_field.value = ""
        self.plate_number_field.value = ""
        self.description_field.value = ""
        self.page.update()


def main(page: ft.Page):
    app = PenaltySystem(page)


if __name__ == "__main__":
    ft.app(target=main)
