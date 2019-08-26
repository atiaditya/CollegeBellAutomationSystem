#Importing Required Modules
import tkinter as tk
from tkinter import *
from tkinter import ttk
import sqlite3
import winsound
from datetime import datetime


#Global Declarations
LARGE_FONT= ("Ariel", 28,'bold')
MEDIUM_FONT = ("Ariel", 20,'bold')
SMALL_FONT = ("Times New Roman",16)
AA = 'all_alarms'
ACTA = 'active_alarms'
AAN = 'all_alarm_names'
ACTAN = 'active_alarm_names'


#Creating Required DataBases
conn = sqlite3.connect('CBAS.sqlite')
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS ALL_ALARMS (name VARCHAR, ringtime VARCHAR, belltype VARCHAR)')
cur.execute('CREATE TABLE IF NOT EXISTS ACTIVE_ALARMS (name VARCHAR, ringtime VARCHAR, belltype VARCHAR)')
cur.execute('CREATE TABLE IF NOT EXISTS ACTIVE_ALARM_NAMES (name VARCHAR)')
cur.execute('CREATE TABLE IF NOT EXISTS ALL_ALARM_NAMES (name VARCHAR)')
conn.commit()
conn.close()


class CBAS(tk.Tk):

	def __init__(self):

		tk.Tk.__init__(self)
		self.container = tk.Frame(self)
		self.container.pack(side="top", fill="both", expand = True)
		self.geometry("1880x800")
		self.container.config(bg = 'black')
		self.frame = None
		self.show_frame(HomePage)
		self.after(0, self.alarm)


	def show_frame(self, cont):

		self.new_frame = cont(self.container, self)
		if self.frame is not None:
			self.frame.destroy()
		self.frame = self.new_frame
		self.frame.pack(side="top", fill="both", expand = True)


	def store_in_db(self, periods, table_name):

		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()

		if(table_name == AA):
			for row in periods:
				name, ringtime, belltype = str(row).split(',')
				cur.execute('INSERT INTO ALL_ALARMS (name, ringtime, belltype) VALUES (?, ?, ?)',(name, ringtime, belltype))
			cur.execute('INSERT INTO ALL_ALARM_NAMES (name) VALUES (?)',(name,))

		elif(table_name == ACTA):
			for row in periods:
				name, ringtime, belltype = str(row).split(',')
				cur.execute('INSERT INTO ACTIVE_ALARMS (name, ringtime, belltype) VALUES (?, ?, ?)',(name, ringtime, belltype))
			cur.execute('INSERT INTO ACTIVE_ALARM_NAMES (name) VALUES (?)',(name,))

		conn.commit()
		conn.close()
		HomePage(self.container, self)
		self.show_frame(HomePage)


	def retrieve_from_db(self, table_name):

		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()

		if(table_name == AA):
			cur.execute('SELECT * FROM ALL_ALARMS')
		elif(table_name == ACTA):
			cur.execute('SELECT * FROM ACTIVE_ALARMS')
		elif(table_name == AAN):
			cur.execute('SELECT * FROM ALL_ALARM_NAMES')
		else:
			cur.execute('SELECT * FROM ACTIVE_ALARM_NAMES')

		self.data = cur.fetchall()
		conn.commit()
		conn.close()
		return self.data


	def alarm(self):

		active_alarms_data = self.retrieve_from_db(ACTA)
		active_alarm_names = self.retrieve_from_db(ACTAN)
		#print(active_data)
		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()

		for row in active_alarms_data:
			name = name.strip(",('")
			name,ringtime_str,belltype = row
			ringtime_str = ringtime_str.strip(",'")
			belltype = belltype.strip(",)'")		
			current_time = datetime.now().time()
			ringtime = datetime.strptime(ringtime_str, '%H::%M')
			if(ringtime >= current_time):
				frequency = 1000
				duration = 10000
				if(belltype == 'long'):
					frequency = 5000

				if(belltype == 'short'):
					frequency = 2500
				winsound.Beep(frequency, duration)

			else:
				print(ringtime)
				cur.execute('DELETE FROM ACTIVE WHERE name = (?) AND ringtime = (?) AND belltype = (?)', (name, ringtime, belltype))
				

		for row in active_user_data:
			name, = row
			cur.execute('SELECT * FROM ACTIVE WHERE name = (?)', (name,))
			data = cur.fetchall()
			if not data:
				print('good boy')
				cur.execute('DELETE FROM ACTIVE_USER WHERE name = (?)', (name,))
				HomePage(self.container, self)
			else:
				print('hi')
		conn.commit()
		conn.close()

		self.after(60000, self.alarm)


class HomePage(tk.Frame):

	def __init__(self, parent, controller):

		tk.Frame.__init__(self, parent)
		self.config(bg = '#9cc0d9')
		#logo = tk.PhotoImage(file = 'C:\\Users\\Lenovo\\Desktop\\dribbble.gif')
		l = tk.Label(self, text = "HomePage",bg='#a79cd9',font=LARGE_FONT,borderwidth=5,relief = 'raised')
		l.grid(row=0,column=0,sticky = W+E,columnspan=6,ipadx = 600,pady = 5,ipady = 5,padx = 5)
		all_label = ttk.Label(self, text = 'PRESETS',anchor='center',font=MEDIUM_FONT,background = '#9cd9b3',borderwidth=5,relief = 'sunken')
		all_label.grid(row=1,column=0,sticky=N+S+W+E,columnspan=3,pady =5,padx=5,ipady = 3)
		active_label = ttk.Label(self, text = 'ACTIVE',anchor='center',font=MEDIUM_FONT,background = '#9cd9b3',borderwidth=5,relief = 'sunken')
		active_label.grid(row=1,column=3,sticky=N+S+W+E,columnspan=3,pady =5,padx=5,ipady = 3)
		all_user_data = controller.retrieve_allalarms_user()
		active_user_data  = controller.retrieve_active_user()
		self.all = tk.Listbox(self, selectmode = 'multiple',font = SMALL_FONT)
		self.all.insert('end', *all_user_data)
		self.all.grid(row=2,column=0,sticky = N+S+W+E,columnspan=3,rowspan=5,ipady=160,pady =10,padx=10)
		self.active = tk.Listbox(self, selectmode = 'multiple')
		self.active.insert('end', *active_user_data)
		self.active.grid(row=2,column=3,sticky=N+E+W+S,columnspan=3,pady =10,padx=10)
		all_scrollbar = tk.Scrollbar(self.all, orient  = 'vertical')
		all_scrollbar.config(command = self.all.yview)
		all_scrollbar.pack(side="right", fill="y")
		self.all.config(yscrollcommand = all_scrollbar.set)

		refresh = ttk.Button(self, text = "Refresh", command = lambda : self.modify(controller))
		refresh.grid(row=3,column=5,sticky=N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)
		showlabel = tk.Label(self, text = 'Enter alarm name :', font = SMALL_FONT, bg = '#9cc0d9')
		showlabel.grid(row=4,column = 3,sticky=N+E+S,pady = 5,padx=10,ipadx = 1,ipady = 3)
		alarm_name = ttk.Entry(self)
		alarm_name.grid(row = 4,column = 4,sticky=N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)
		show = ttk.Button(self, text = 'Show', command = lambda : self.show_details(alarm_name.get()))
		show.grid(row=4,column=5,sticky = N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)
		s = ttk.Style()
		s.configure('TButton', font = SMALL_FONT)
		add = ttk.Button(self, text = 'Set', command = lambda : self.add(controller))
		add.grid(row=7,column=0,sticky=E+W,pady = 5,padx=10,ipadx = 1,ipady = 1)
		new = ttk.Button(self,text = 'New', command = lambda : controller.show_frame(New))
		new.grid(row = 7,column = 1,pady = 5,padx=10,ipadx = 1,ipady = 1,sticky = E+W)
		self.e = tk.Text(self, height = 20)
		self.e.grid(row=5,column=3,sticky = E+W,columnspan = 3,rowspan = 3,pady = 5,padx=5)
		remove1 = ttk.Button(self, text = 'Remove', command = lambda: self.delete_items_all())
		remove1.grid(row = 7, column = 2,sticky = W+E,pady = 5,padx=10,ipadx = 1,ipady = 1)
		remove2 = ttk.Button(self, text = 'Remove', command = lambda : self.delete_items_active())
		remove2.grid(row = 3, column = 4, sticky = N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)
		self.modify(controller)
		'''all_user_data = controller.retrieve_allalarms_user()
		active_user_data  = controller.retrieve_active_user()
		self.alarm_var = tk.StringVar()
		self.alarm_menu = tk.OptionMenu(self, self.alarm_var, *all_user_data)
		self.alarm_menu.pack()
		self.active_var = tk.StringVar()
		self.active_menu = tk.OptionMenu(self, self.alarm_var, *all_user_data)
		self.alarm_menu.pack()
		self.modify_options(controller)

	def modify_options(self, controller):
		self.alarm_var.set('')
		self.alarm_menu['menu'].delete(0, 'end')
		all_user_data=controller.retrieve_allalarms_user()
		for choice in all_user_data:
			self.alarm_menu['menu'].add_command(label=choice, command=tk._setit(self.alarm_var, choice))'''
	def modify(self, controller):
		print('Hii')
		all_user_data = controller.retrieve_allalarms_user()
		
		active_user_data  = controller.retrieve_active_user()
		#print(active_user_data)
		self.all.delete(0, 'end')
		#print(all_user_data)
		self.all.insert('end', *all_user_data)
		self.active.delete(0, 'end')
		self.active.insert('end', *active_user_data)

	def add(self, controller):

		active_user_data = controller.retrieve_active_user()
		print(active_user_data)
		selected = self.all.curselection()
		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()
		for i in selected:
			
			if self.all.get(i) not in active_user_data:
				cur.execute('INSERT INTO ACTIVE_USER (name) VALUES (?)',(self.all.get(i)))
				cur.execute('SELECT * FROM ALLALARMS  WHERE name = (?)',(self.all.get(i)))
				selecteddata = cur.fetchall()
				for row in selecteddata:
					name, ringtime, belltype = row
					cur.execute('INSERT INTO ACTIVE VALUES (?,?,?)',(name, ringtime, belltype))
			conn.commit()
		conn.close()

	def show_details(self, name):

		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM ALLALARMS WHERE name = (?)', (name,))
		data = cur.fetchall()
		if self.e is not None:
			self.e.destroy()
		self.e = tk.Text(self, height = 20, width = 40)
		self.e.config(state = 'normal')

		self.e.delete(1.0, 'end')
		for row in data:
			
			self.e.insert('end', str(row)+'\n')
		self.e.config(state = 'disabled')
		self.e.grid(row=5,column=3,sticky = E+W,columnspan = 3,rowspan = 3,pady = 5,padx=5)
		conn.commit()
		conn.close()

	def delete_items_all(self):
		sel = self.all.curselection()
		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()
		for i in sel[::-1]:
			cur.execute('DELETE FROM ALLALARMS WHERE name = (?)', (self.all.get(i)))
			cur.execute('DELETE FROM ALLALARMS_USER WHERE name = (?)', (self.all.get(i)))
			cur.execute('DELETE FROM ACTIVE WHERE name = (?)', (self.all.get(i)))
			cur.execute('DELETE FROM ACTIVE_USER WHERE name = (?)', (self.all.get(i)))
			self.all.delete(i)
		conn.commit()
		conn.close()

	def delete_items_active(self):
		sel = self.active.curselection()
		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()
		for i in sel[::-1]:
			cur.execute('DELETE FROM ACTIVE WHERE name = (?)', (self.all.get(i)))
			cur.execute('DELETE FROM ACTIVE_USER WHERE name = (?)', (self.all.get(i)))
			self.active.delete(i)
		conn.commit()
		conn.close()

class New(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.config(bg = '#9cc0d9')
		n = tk.Label(self, text = 'Name :', font = SMALL_FONT, bg = '#9cc0d9')
		n.grid(row = 0)
		ne = ttk.Entry(self, font = SMALL_FONT)
		ne.grid(row = 0,column = 1,sticky=N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)
		number = tk.Label(self, text = 'No of periods :', font = SMALL_FONT, bg = '#9cc0d9')
		number.grid(row = 0, column = 2)
		numbere = ttk.Entry(self, font = SMALL_FONT)
		numbere.grid(row = 0,column = 3,sticky=N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)
		submit = ttk.Button(self, text = "Submit", command = lambda : self.submit1(ne.get(), int(numbere.get()), controller))
		submit.grid(row = 0, column = 4)
		back = ttk.Button(self, text = "Back", command = lambda : controller.show_frame(HomePage))
		back.grid(row = 0, column = 5, padx = 5)
		
	def submit1(self, name, no_of_periods, controller):

		self.l = []
		hours_options = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09']
		hours_options.extend([str(i) for i in range(10,24)])
		minutes_options = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09']
		minutes_options.extend([str(i) for i in range(10,60)])
		belltypes  = ['short', 'long']
		for i in range(no_of_periods):
			hours_var = tk.StringVar()
			minutes_var  = tk.StringVar()
			belltype_var = tk.StringVar()
			hour_menu = ttk.Combobox(self, textvariable=hours_var, values=hours_options, state = 'readonly').grid(row = i+1,pady = 3)
			minute_menu = ttk.Combobox(self, textvariable = minutes_var, values = minutes_options, state = 'readonly').grid(row = i+1, column = 1,pady=3)
			belltype_menu = ttk.Combobox(self, textvariable = belltype_var, values = belltypes, state = 'readonly').grid(row = i+1, column = 2,pady=3)
			hours_var.set(hours_options[0])
			minutes_var.set(minutes_options[0])
			belltype_var.set(belltypes[0])
			self.l.append((hours_var, minutes_var, belltype_var))
		submit = ttk.Button(self, text = "Submit", command = lambda : self.submit2(name, controller))
		no_of_periods += 1
		submit.grid(row = no_of_periods)

	def submit2(self, name, controller):
		#print(name)
		periods = [name + ','+ hours_var.get()+'::'+minutes_var.get()+','+belltype_var.get() for hours_var,minutes_var,belltype_var in self.l]
		controller.store_all(periods)
		

app = CBAS()
app.mainloop()