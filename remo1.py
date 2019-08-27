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
hours_options = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09']
hours_options.extend([str(i) for i in range(10,24)])
minutes_options = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09']
minutes_options.extend([str(i) for i in range(10,60)])
belltypes  = ['short', 'long']


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


	def store_in_db(self, periods, table_name, alarm_name):

		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()

		if(table_name == AA):

			cur.executemany('INSERT INTO ALL_ALARMS VALUES (?,?,?)', periods)
			conn.commit()
			cur.execute('INSERT INTO ALL_ALARM_NAMES VALUES (?)',(alarm_name,))
			conn.commit()

		elif(table_name == ACTA):

			cur.executemany('INSERT INTO ACTIVE_ALARMS VALUES (?,?,?)', periods)
			conn.commit()
			cur.execute('INSERT INTO ACTIVE_ALARM_NAMES VALUES (?)',(alarm_name,))
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


	def delete_from_alarms(self, name, ringtime, belltype, table_name):

		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()

		if(table_name == AA):
			cur.execute('DELETE FROM ALL_ALARMS WHERE name = (?) AND ringtime = (?) AND belltype = (?)', (name, ringtime, belltype))
			conn.commit()

		cur.execute('DELETE FROM ACTIVE_ALARMS WHERE name = (?) AND ringtime = (?) AND belltype = (?)', (name, ringtime, belltype))
		conn.commit()
		conn.close()


	def delete_from_names(self, alarm_name, table_name):

		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()
		if(table_name == AA):

			cur.execute('DELETE FROM ALL_ALARM_NAMES WHERE name = (?)', (alarm_name,))
			conn.commit()

		cur.execute('DELETE FROM ACTIVE_ALARM_NAMES WHERE name = (?)', (alarm_name,))
		conn.commit()
		conn.close()


	def retrieve_alarms_by_name(self, alarm_name):

		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM ALL_ALARMS WHERE name = (?)', (alarm_name,))
		data = cur.fetchall()
		conn.commit()
		conn.close()

		return data


	def alarm(self):

		self.active_alarms_data = self.retrieve_from_db(ACTA)
		self.active_alarm_names = self.retrieve_from_db(ACTAN)
		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()

		for row in self.active_alarms_data:
			
			name,ringtime_str,belltype = row
			name = name.strip(",('")
			ringtime_str = ringtime_str.strip(",'")
			belltype = belltype.strip(",)'")		
			current_time = datetime.now().time()
			ringtime = datetime.strptime(ringtime_str, '%H::%M').time()
			print(ringtime, current_time)
			if(current_time >= ringtime):
				
				frequency = 1000
				duration = 10000
				if(belltype == 'long'):
					frequency = 5000

				if(belltype == 'short'):
					frequency = 2500

				winsound.Beep(frequency, duration)
				cur.execute('DELETE FROM ACTIVE_ALARMS WHERE name = (?) AND ringtime = (?) AND belltype = (?)', (name, ringtime_str, belltype))
				conn.commit()
				cur.execute('SELECT COUNT(*) FROM ACTIVE_ALARMS WHERE name = (?)', (name,))
				conn.commit()
				[(name_count,)] = cur.fetchall()

				if(name_count == 0):

					cur.execute('DELETE FROM ACTIVE_ALARM_NAMES WHERE name = (?)', (name,))
					conn.commit()
					#HomePage(self.container, self)

		conn.close()
		self.after(30000, self.alarm)


class HomePage(tk.Frame):

	def __init__(self, parent, controller):

		tk.Frame.__init__(self, parent)
		self.config(bg = '#9cc0d9')
		self.controller = controller

		#Home
		home_label = tk.Label(self, text = "HomePage",bg='#a79cd9',font=LARGE_FONT,borderwidth=5,relief = 'raised')
		home_label.grid(row=0,column=0,sticky = W+E,columnspan=6,ipadx = 600,pady = 5,ipady = 5,padx = 5)

		#All Alarms list and corresponding options.
		aan_label = ttk.Label(self, text = 'PRESETS',anchor='center',font=MEDIUM_FONT,background = '#9cd9b3',borderwidth=5,relief = 'sunken')
		aan_label.grid(row=1,column=0,sticky=N+S+W+E,columnspan=3,pady =5,padx=5,ipady = 3)

		aan_data = controller.retrieve_from_db(AAN)

		self.aan_list = tk.Listbox(self, selectmode = 'multiple', font = SMALL_FONT)
		self.aan_list.insert('end', *aan_data)
		self.aan_list.grid(row=2,column=0,sticky = N+S+W+E,columnspan=3,rowspan=5,ipady=160,pady =10,padx=10)

		aan_scrollbar = tk.Scrollbar(self.aan_list, orient  = 'vertical')
		aan_scrollbar.config(command = self.aan_list.yview)
		aan_scrollbar.pack(side="right", fill="y")
		self.aan_list.config(yscrollcommand = aan_scrollbar.set)

		aan_remove = ttk.Button(self, text = 'Remove', command = lambda: self.delete_from_aan_list())
		aan_remove.grid(row = 7, column = 2,sticky = W+E,pady = 5,padx=10,ipadx = 1,ipady = 1)

		set_active = ttk.Button(self, text = 'Set', command = lambda : self.set_to_active())
		set_active.grid(row=7,column=0,sticky=E+W,pady = 5,padx=10,ipadx = 1,ipady = 1)

		new = ttk.Button(self,text = 'New', command = lambda : self.controller.show_frame(New))
		new.grid(row = 7,column = 1,pady = 5,padx=10,ipadx = 1,ipady = 1,sticky = E+W)


		#Active Alarms list and corresponding options.
		active_label = ttk.Label(self, text = 'ACTIVE',anchor='center',font=MEDIUM_FONT,background = '#9cd9b3',borderwidth=5,relief = 'sunken')
		active_label.grid(row=1,column=3,sticky=N+S+W+E,columnspan=3,pady =5,padx=5,ipady = 3)

		actan_data  = controller.retrieve_from_db(ACTAN)

		self.actan_list = tk.Listbox(self, selectmode = 'multiple')
		self.actan_list.insert('end', *actan_data)
		self.actan_list.grid(row=2,column=3,sticky=N+E+W+S,columnspan=3,pady =10,padx=10)

		refresh = ttk.Button(self, text = "Refresh", command = lambda : self.update_lists())
		refresh.grid(row=3,column=5,sticky=N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)

		actan_remove = ttk.Button(self, text = 'Remove', command = lambda : self.delete_from_actan_list())
		actan_remove.grid(row = 3, column = 4, sticky = N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)

		actan_scrollbar = tk.Scrollbar(self.actan_list, orient  = 'vertical')
		actan_scrollbar.config(command = self.actan_list.yview)
		actan_scrollbar.pack(side="right", fill="y")
		self.actan_list.config(yscrollcommand = actan_scrollbar.set)


		#See what are the ringtimes of particular alarm
		show_label = tk.Label(self, text = 'Enter alarm name :', font = SMALL_FONT, bg = '#9cc0d9')
		show_label.grid(row=4,column = 3,sticky=N+E+S,pady = 5,padx=10,ipadx = 1,ipady = 3)

		alarm_name = ttk.Entry(self)
		alarm_name.grid(row = 4,column = 4,sticky=N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)

		show_button = ttk.Button(self, text = 'Show', command = lambda : self.show_details(alarm_name.get()))
		show_button.grid(row=4,column=5,sticky = N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)

		s = ttk.Style()
		s.configure('TButton', font = SMALL_FONT)
		
	
		self.display_details = tk.Text(self, height = 20)
		self.display_details.grid(row=5,column=3,sticky = E+W,columnspan = 3,rowspan = 3,pady = 5,padx=5)
		
		self.update_lists()


	def update_lists(self):

		aan_data_updated = self.controller.retrieve_from_db(AAN)
		actan_data_updated  = self.controller.retrieve_from_db(ACTAN)

		self.aan_list.delete(0, 'end')
		self.aan_list.insert('end', *aan_data_updated)

		self.actan_list.delete(0, 'end')
		self.actan_list.insert('end', *actan_data_updated)


	def set_to_active(self):

		actan_data = self.controller.retrieve_from_db(ACTAN)
		selected_alarms = self.aan_list.curselection()
		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()

		for i in selected_alarms:
			
			if self.aan_list.get(i) not in actan_data:

				cur.execute('INSERT INTO ACTIVE_ALARM_NAMES (name) VALUES (?)',(self.aan_list.get(i)))
				conn.commit()
				cur.execute('SELECT * FROM ALL_ALARMS WHERE name = (?)',(self.aan_list.get(i)))
				conn.commit()
				selected_data = cur.fetchall()

				for row in selected_data:

					name, ringtime, belltype = row
					cur.execute('INSERT INTO ACTIVE_ALARMS VALUES (?,?,?)',(name, ringtime, belltype))
					conn.commit()

		self.update_lists()
		conn.close()


	def show_details(self, alarm_name):

		data = self.controller.retrieve_alarms_by_name(alarm_name)

		if self.display_details is not None:
			self.display_details.destroy()

		self.display_details = tk.Text(self, height = 20, width = 40)
		self.display_details.config(state = 'normal')
		self.display_details.delete(1.0, 'end')

		for row in data:
			self.display_details.insert('end', str(row)+'\n')

		self.display_details.config(state = 'disabled')
		self.display_details.grid(row=5,column=3,sticky = E+W,columnspan = 3,rowspan = 3,pady = 5,padx=5)


	def delete_from_aan_list(self):

		selected_alarms = self.aan_list.curselection()
		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()

		for i in selected_alarms[::-1]:

			cur.execute('DELETE FROM ALL_ALARMS WHERE name = (?)', (self.aan_list.get(i)))
			conn.commit()
			cur.execute('DELETE FROM ALL_ALARM_NAMES WHERE name = (?)', (self.aan_list.get(i)))
			conn.commit()
			cur.execute('DELETE FROM ACTIVE_ALARMS WHERE name = (?)', (self.aan_list.get(i)))
			conn.commit()
			cur.execute('DELETE FROM ACTIVE_ALARM_NAMES WHERE name = (?)', (self.aan_list.get(i)))
			conn.commit()
			self.aan_list.delete(i)

		self.update_lists()
		conn.close()


	def delete_from_actan_list(self):

		selected_alarms = self.actan_list.curselection()
		conn = sqlite3.connect('CBAS.sqlite')
		cur = conn.cursor()

		for i in selected_alarms[::-1]:

			cur.execute('DELETE FROM ACTIVE_ALARMS WHERE name = (?)', (self.actan_list.get(i)))
			conn.commit()
			cur.execute('DELETE FROM ACTIVE_ALARM_NAMES WHERE name = (?)', (self.actan_list.get(i)))
			conn.commit()
			self.actan_list.delete(i)

		self.update_lists()
		conn.close()



class New(tk.Frame):

	def __init__(self, parent, controller):

		self.controller = controller
		self.last_button = None
		self.menu_items_list = []
		tk.Frame.__init__(self, parent)
		self.config(bg = '#9cc0d9')

		self.name = tk.Label(self, text = 'Name :', font = SMALL_FONT, bg = '#9cc0d9')
		self.name.grid(row = 0)

		self.name_entry = ttk.Entry(self, font = SMALL_FONT)
		self.name_entry.grid(row = 0,column = 1,sticky=N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)

		no_of_periods = tk.Label(self, text = 'No of periods :', font = SMALL_FONT, bg = '#9cc0d9')
		no_of_periods.grid(row = 0, column = 2)

		no_of_periods_entry = ttk.Entry(self, font = SMALL_FONT)
		no_of_periods_entry.grid(row = 0,column = 3,sticky=N+E+W+S,pady = 5,padx=10,ipadx = 1,ipady = 3)

		submit_top = ttk.Button(self, text = "Submit", command = lambda : self.on_click_submit_top(int(no_of_periods_entry.get() )))
		submit_top.grid(row = 0, column = 4)

		back = ttk.Button(self, text = "Back", command = lambda : self.controller.show_frame(HomePage))
		back.grid(row = 0,column = 5,padx = 5)
		

	def on_click_submit_top(self, no_of_periods):

		self.current_ring_times = []
	
		if self.last_button is not None:
			self.last_button.destroy()

		while(self.menu_items_list):
			menu_item = self.menu_items_list.pop()
			menu_item.destroy()

		for i in range(no_of_periods):

			hours_var = tk.StringVar()
			minutes_var  = tk.StringVar()
			belltype_var = tk.StringVar()

			hour_menu = ttk.Combobox(self, textvariable=hours_var, values=hours_options, state = 'readonly')
			hour_menu.grid(row = i+1,pady = 3)

			minute_menu = ttk.Combobox(self, textvariable = minutes_var, values = minutes_options, state = 'readonly')
			minute_menu.grid(row = i+1, column = 1,pady=3)

			belltype_menu = ttk.Combobox(self, textvariable = belltype_var, values = belltypes, state = 'readonly')
			belltype_menu.grid(row = i+1, column = 2,pady=3)

			hours_var.set(hours_options[0])
			minutes_var.set(minutes_options[0])
			belltype_var.set(belltypes[0])

			self.menu_items_list.extend([hour_menu, minute_menu, belltype_menu])
			self.current_ring_times.append((hours_var, minutes_var, belltype_var))

		submit_bottom = ttk.Button(self, text = "Submit", command = lambda : self.on_click_submit_bottom())
		no_of_periods += 1
		submit_bottom.grid(row = no_of_periods)
		self.last_button = submit_bottom


	def on_click_submit_bottom(self):

		self.name = self.name_entry.get()
		#print(name)
		periods = [ (self.name, hours_var.get()+'::'+minutes_var.get(), belltype_var.get()) for hours_var,minutes_var,belltype_var in self.current_ring_times]
		print(periods)
		self.controller.store_in_db(periods, AA, self.name)
		

app = CBAS()
app.mainloop()