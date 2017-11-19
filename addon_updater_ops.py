# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.app.handlers import persistent
import os

# updater import, import safely
# Prevents popups for users with invalid python installs e.g. missing libraries
try:
	from .addon_updater import Updater as updater
except Exception as e:
	print("ERROR INITIALIZING UPDATER")
	print(str(e))
	class Singleton_updater_none(object):
		def __init__(self):
			self.addon = None
			self.verbose = False
			self.invalidupdater = True # used to distinguish bad install
			self.error = None
			self.error_msg = None
			self.async_checking = None
	updater = Singleton_updater_none()
	updater.error = "Error initializing updater module"
	updater.error_msg = str(e)

# Must declare this before classes are loaded
# otherwise the bl_idname's will not match and have errors.
# Must be all lowercase and no spaces
updater.addon = "cats_blender_plugin"


# -----------------------------------------------------------------------------
# Updater operators
# -----------------------------------------------------------------------------


# simple popup for prompting checking for update & allow to install if available
class addon_updater_install_popup(bpy.types.Operator):
	"""Check and install update if available"""
	bl_label = "Update {x} addon".format(x=updater.addon)
	bl_idname = updater.addon+".updater_install_popup"
	bl_description = "Popup menu to check and display current updates available"

	# if true, run clean install - ie remove all files before adding new
	# equivalent to deleting the addon and reinstalling, except the
	# updater folder/backup folder remains
	clean_install = bpy.props.BoolProperty(
		name="Clean install",
		description="If enabled, completely clear the addon's folder before installing new update, creating a fresh install",
		default=False,
		options={'HIDDEN'}
	)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		if updater.invalidupdater == True:
			layout.label("Updater module error")
			return
		if updater.update_ready == True:
			col = layout.column()
			col.scale_y = 0.7
			col.label("Update ready! Press OK to install "\
						+str(updater.update_version),icon="LOOP_FORWARDS")
			col.label("or click outside window to defer",icon="BLANK1")
			# could offer to remove popups here, but window will not redraw
			# so may be confusing to the user/look like a bug
			# row = layout.row()
			# row.label("Prevent future popups:")
			# row.operator(addon_updater_ignore.bl_idname,text="Ignore update")
		elif updater.update_ready == False:
			col = layout.column()
			col.scale_y = 0.7
			col.label("No updates available")
			col.label("Press okay to dismiss dialog")
			# add option to force install
		else:
			# case: updater.update_ready = None
			# we have not yet checked for the update
			layout.label("Check for update now?")

		# potentially in future, could have UI for 'check to select old version'
		# to revert back to.

	def execute(self,context):

		# in case of error importing updater
		if updater.invalidupdater == True:
			return {'CANCELLED'}

		if updater.manual_only==True:
			bpy.ops.wm.url_open(url=updater.website)
		elif updater.update_ready == True:
			res = updater.run_update(
							force=False,
							callback=post_update_callback,
							clean=self.clean_install)
			# should return 0, if not something happened
			if updater.verbose:
				if res==0: print("Updater returned successful")
				else: print("Updater returned "+str(res)+", error occurred")
		elif updater.update_ready == None:
			(update_ready, version, link) = updater.check_for_update(now=True)
			
			# re-launch this dialog
			atr = addon_updater_install_popup.bl_idname.split(".")
			getattr(getattr(bpy.ops, atr[0]),atr[1])('INVOKE_DEFAULT')
		else:
			if updater.verbose:print("Doing nothing, not ready for update")
		return {'FINISHED'}


# User preference check-now operator
class addon_updater_check_now(bpy.types.Operator):
	bl_label = "Check now for "+updater.addon+" update"
	bl_idname = updater.addon+".updater_check_now"
	bl_description = "Check now for an update to the {x} addon".format(
														x=updater.addon)

	def execute(self,context):

		# in case of error importing updater
		if updater.invalidupdater == True:
			return {'CANCELLED'}

		if updater.async_checking == True and updater.error == None:
			# Check already happened
			# Used here to just avoid constant applying settings below
			# Ignoring if error, to prevent being stuck on the error screen
			return {'CANCELLED'}

		# apply the UI settings
		settings = context.user_preferences.addons[__package__].preferences
		updater.set_check_interval(enable=settings.auto_check_update,
					months=settings.updater_intrval_months,
					days=settings.updater_intrval_days,
					hours=settings.updater_intrval_hours,
					minutes=settings.updater_intrval_minutes
					) # optional, if auto_check_update 
		
		# input is an optional callback function
		# this function should take a bool input, if true: update ready
		# if false, no update ready
		updater.check_for_update_now()

		return {'FINISHED'}


class addon_updater_update_now(bpy.types.Operator):
	bl_label = "Update "+updater.addon+" addon now"
	bl_idname = updater.addon+".updater_update_now"
	bl_description = "Update to the latest version of the {x} addon".format(
														x=updater.addon)

	# if true, run clean install - ie remove all files before adding new
	# equivalent to deleting the addon and reinstalling, except the
	# updater folder/backup folder remains
	clean_install = bpy.props.BoolProperty(
		name="Clean install",
		description="If enabled, completely clear the addon's folder before installing new update, creating a fresh install",
		default=False,
		options={'HIDDEN'}
	)

	def execute(self,context):

		# in case of error importing updater
		if updater.invalidupdater == True:
			return {'CANCELLED'}

		if updater.manual_only == True:
			bpy.ops.wm.url_open(url=updater.website)
		if updater.update_ready == True:
			# if it fails, offer to open the website instead
			try:
				res = updater.run_update(
								force=False,
								callback=post_update_callback,
								clean=self.clean_install)

				# should return 0, if not something happened
				if updater.verbose:
					if res==0: print("Updater returned successful")
					else: print("Updater returned "+str(res)+", error occurred")
			except:
				atr = addon_updater_install_manually.bl_idname.split(".")
				getattr(getattr(bpy.ops, atr[0]),atr[1])('INVOKE_DEFAULT')
		elif updater.update_ready == None:
			(update_ready, version, link) = updater.check_for_update(now=True)
			# re-launch this dialog
			atr = addon_updater_install_popup.bl_idname.split(".")
			getattr(getattr(bpy.ops, atr[0]),atr[1])('INVOKE_DEFAULT')
			
		elif updater.update_ready == False:
			self.report({'INFO'}, "Nothing to update")
		else:
			self.report({'ERROR'}, "Encountered problem while trying to update")

		return {'FINISHED'}


class addon_updater_update_target(bpy.types.Operator):
	bl_label = updater.addon+" addon version target"
	bl_idname = updater.addon+".updater_update_target"
	bl_description = "Install a targeted version of the {x} addon".format(
														x=updater.addon)

	def target_version(self, context):
		# in case of error importing updater
		if updater.invalidupdater == True:
			ret = []

		ret = []
		i=0
		for tag in updater.tags:
			ret.append( (tag,tag,"Select to install "+tag) )
			i+=1
		return ret

	target = bpy.props.EnumProperty(
		name="Target version",
		description="Select the version to install",
		items=target_version
		)

	# if true, run clean install - ie remove all files before adding new
	# equivalent to deleting the addon and reinstalling, except the
	# updater folder/backup folder remains
	clean_install = bpy.props.BoolProperty(
		name="Clean install",
		description="If enabled, completely clear the addon's folder before installing new update, creating a fresh install",
		default=False,
		options={'HIDDEN'}
	)

	@classmethod
	def poll(cls, context):
		if updater.invalidupdater == True: return False
		return updater.update_ready != None and len(updater.tags)>0

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		if updater.invalidupdater == True:
			layout.label("Updater error")
			return
		split = layout.split(percentage=0.66)
		subcol = split.column()
		subcol.label("Select install version")
		subcol = split.column()
		subcol.prop(self, "target", text="")


	def execute(self,context):

		# in case of error importing updater
		if updater.invalidupdater == True:
			return {'CANCELLED'}

		res = updater.run_update(
						force=False,
						revert_tag=self.target,
						callback=post_update_callback,
						clean=self.clean_install)

		# should return 0, if not something happened
		if updater.verbose:
			if res==0: print("Updater returned successful")
			else: print("Updater returned "+str(res)+", error occurred")
			return {'CANCELLED'}

		return {'FINISHED'}


class addon_updater_install_manually(bpy.types.Operator):
	"""As a fallback, direct the user to download the addon manually"""
	bl_label = "Install update manually"
	bl_idname = updater.addon+".updater_install_manually"
	bl_description = "Proceed to manually install update"

	error = bpy.props.StringProperty(
		name="Error Occurred",
		default="",
		options={'HIDDEN'}
		)

	def invoke(self, context, event):
		return context.window_manager.invoke_popup(self)

	def draw(self, context):
		layout = self.layout

		if updater.invalidupdater == True:
			layout.label("Updater error")
			return

		# use a "failed flag"? it shows this label if the case failed.
		if self.error!="":
			col = layout.column()
			col.scale_y = 0.7
			col.label("There was an issue trying to auto-install",icon="ERROR")
			col.label("Press the download button below and install",icon="BLANK1")
			col.label("the zip file like a normal addon.",icon="BLANK1")
		else:
			col = layout.column()
			col.scale_y = 0.7
			col.label("Install the addon manually")
			col.label("Press the download button below and install")
			col.label("the zip file like a normal addon.")

		# if check hasn't happened, i.e. accidentally called this menu
		# allow to check here

		row = layout.row()

		if updater.update_link != None:
			row.operator("wm.url_open",text="Direct download").url=\
					updater.update_link
		else:
			row.operator("wm.url_open",text="(failed to retrieve)")
			row.enabled = False

			if updater.website != None:
				row = layout.row()
				row.operator("wm.url_open",text="Open website").url=\
						updater.website
			else:
				row = layout.row()
				row.label("See source website to download the update")

	def execute(self,context):

		return {'FINISHED'}


class addon_updater_updated_successful(bpy.types.Operator):
	"""Addon in place, popup telling user it completed or what went wrong"""
	bl_label = "Installation Report"
	bl_idname = updater.addon+".updater_update_successful"
	bl_description = "Update installation response"
	bl_options = {'REGISTER', 'UNDO'}

	error = bpy.props.StringProperty(
		name="Error Occurred",
		default="",
		options={'HIDDEN'}
		)

	def invoke(self, context, event):
		return context.window_manager.invoke_props_popup(self, event)

	def draw(self, context):
		layout = self.layout

		if updater.invalidupdater == True:
			layout.label("Updater error")
			return

		saved = updater.json
		if self.error != "":
			col = layout.column()
			col.scale_y = 0.7
			col.label("Error occurred, did not install", icon="ERROR")
			col.label(updater.error_msg, icon="BLANK1")
			rw = col.row()
			rw.scale_y = 2
			rw.operator("wm.url_open",
				text="Click for manual download.",
				icon="BLANK1"
				).url=updater.website
			# manual download button here
		elif updater.auto_reload_post_update == False:
			# tell user to restart blender
			if "just_restored" in saved and saved["just_restored"] == True:
				col = layout.column()
				col.scale_y = 0.7
				col.label("Addon restored", icon="RECOVER_LAST")
				col.label("Restart blender to reload.",icon="BLANK1")
				updater.json_reset_restore()
			else:
				col = layout.column()
				col.scale_y = 0.7
				col.label("Addon successfully installed", icon="FILE_TICK")
				col.label("Restart blender to reload.", icon="BLANK1")

		else:
			# reload addon, but still recommend they restart blender
			if "just_restored" in saved and saved["just_restored"] == True:
				col = layout.column()
				col.scale_y = 0.7
				col.label("Addon restored", icon="RECOVER_LAST")
				col.label("Consider restarting blender to fully reload.",icon="BLANK1")
				updater.json_reset_restore()
			else:
				col = layout.column()
				col.scale_y = 0.7
				col.label("Addon successfully installed", icon="FILE_TICK")
				col.label("Consider restarting blender to fully reload.", icon="BLANK1")
	
	def execut(self, context):
		return {'FINISHED'}


class addon_updater_restore_backup(bpy.types.Operator):
	"""Restore addon from backup"""
	bl_label = "Restore backup"
	bl_idname = updater.addon+".updater_restore_backup"
	bl_description = "Restore addon from backup"

	@classmethod
	def poll(cls, context):
		try:
			return os.path.isdir(os.path.join(updater.stage_path,"backup"))
		except:
			return False
	
	def execute(self, context):
		# in case of error importing updater
		if updater.invalidupdater == True:
			return {'CANCELLED'}
		updater.restore_backup()
		return {'FINISHED'}


class addon_updater_ignore(bpy.types.Operator):
	"""Prevent future update notice popups"""
	bl_label = "Ignore update"
	bl_idname = updater.addon+".updater_ignore"
	bl_description = "Ignore update to prevent future popups"

	@classmethod
	def poll(cls, context):
		if updater.invalidupdater == True:
			return False
		elif updater.update_ready == True:
			return True
		else:
			return False
	
	def execute(self, context):
		# in case of error importing updater
		if updater.invalidupdater == True:
			return {'CANCELLED'}
		updater.ignore_update()
		self.report({"INFO"},"Open addon preferences for updater options")
		return {'FINISHED'}


class addon_updater_end_background(bpy.types.Operator):
	"""Stop checking for update in the background"""
	bl_label = "End background check"
	bl_idname = updater.addon+".end_background_check"
	bl_description = "Stop checking for update in the background"

	# @classmethod
	# def poll(cls, context):
	# 	if updater.async_checking == True:
	# 		return True
	# 	else:
	# 		return False
	
	def execute(self, context):
		# in case of error importing updater
		if updater.invalidupdater == True:
			return {'CANCELLED'}
		updater.stop_async_check_update()
		return {'FINISHED'}


# -----------------------------------------------------------------------------
# Handler related, to create popups
# -----------------------------------------------------------------------------


# global vars used to prevent duplicate popup handlers
ran_autocheck_install_popup = False
ran_update_sucess_popup = False

# global var for preventing successive calls 
ran_background_check = False

@persistent
def updater_run_success_popup_handler(scene):
	global ran_update_sucess_popup
	ran_update_sucess_popup = True

	# in case of error importing updater
	if updater.invalidupdater == True:
		return

	try:
		bpy.app.handlers.scene_update_post.remove(
				updater_run_success_popup_handler)
	except:
		pass

	atr = addon_updater_updated_successful.bl_idname.split(".")
	getattr(getattr(bpy.ops, atr[0]),atr[1])('INVOKE_DEFAULT')


@persistent
def updater_run_install_popup_handler(scene):
	global ran_autocheck_install_popup
	ran_autocheck_install_popup = True

	# in case of error importing updater
	if updater.invalidupdater == True:
		return

	try:
		bpy.app.handlers.scene_update_post.remove(
				updater_run_install_popup_handler)
	except:
		pass

	if "ignore" in updater.json and updater.json["ignore"] == True:
		return # don't do popup if ignore pressed
	# elif type(updater.update_version) != type((0,0,0)):
	# 	# likely was from master or another branch, shouldn't trigger popup
	# 	updater.json_reset_restore()
	# 	return
	elif "version_text" in updater.json and "version" in updater.json["version_text"]:
		version = updater.json["version_text"]["version"]
		ver_tuple = updater.version_tuple_from_text(version)
		
		if ver_tuple < updater.current_version:
			# user probably manually installed to get the up to date addon
			# in here. Clear out the update flag using this function
			if updater.verbose:
				print("{} updater: appears user updated, clearing flag".format(\
						updater.addon))
			updater.json_reset_restore()
			return
	atr = addon_updater_install_popup.bl_idname.split(".")
	getattr(getattr(bpy.ops, atr[0]),atr[1])('INVOKE_DEFAULT')
	

# passed into the updater, background thread updater
def background_update_callback(update_ready):
	global ran_autocheck_install_popup

	# in case of error importing updater
	if updater.invalidupdater == True:
		return

	if update_ready != True:
		return
	
	if updater_run_install_popup_handler not in \
				bpy.app.handlers.scene_update_post and \
				ran_autocheck_install_popup==False:
		bpy.app.handlers.scene_update_post.append(
				updater_run_install_popup_handler)
		
		ran_autocheck_install_popup = True


# a callback for once the updater has completed
# Only makes sense to use this if "auto_reload_post_update" == False,
# i.e. don't auto-restart the addon
def post_update_callback(res=None):

	# in case of error importing updater
	if updater.invalidupdater == True:
		return

	if res==None:
		# this is the same code as in conditional at the end of the register function
		# ie if "auto_reload_post_update" == True, comment out this code
		if updater.verbose: print("{} updater: Running post update callback".format(updater.addon))
		#bpy.app.handlers.scene_update_post.append(updater_run_success_popup_handler)

		atr = addon_updater_updated_successful.bl_idname.split(".")
		getattr(getattr(bpy.ops, atr[0]),atr[1])('INVOKE_DEFAULT')
		global ran_update_sucess_popup
		ran_update_sucess_popup = True
	else:
		# some kind of error occured and it was unable to install,
		# offer manual download instead
		atr = addon_updater_updated_successful.bl_idname.split(".")
		getattr(getattr(bpy.ops, atr[0]),atr[1])('INVOKE_DEFAULT',error=res)
	return


# function for asynchronous background check, which *could* be called on register
def check_for_update_background():

	# in case of error importing updater
	if updater.invalidupdater == True:
		return

	global ran_background_check
	if ran_background_check == True:
		# Global var ensures check only happens once
		return
	elif updater.update_ready != None or updater.async_checking == True:
		# Check already happened
		# Used here to just avoid constant applying settings below
		return 

	# apply the UI settings
	addon_prefs = bpy.context.user_preferences.addons.get(__package__, None)
	if not addon_prefs:
		return
	settings = addon_prefs.preferences
	updater.set_check_interval(enable=settings.auto_check_update,
				months=settings.updater_intrval_months,
				days=settings.updater_intrval_days,
				hours=settings.updater_intrval_hours,
				minutes=settings.updater_intrval_minutes
				) # optional, if auto_check_update 
	
	# input is an optional callback function
	# this function should take a bool input, if true: update ready
	# if false, no update ready
	if updater.verbose:
		print("{} updater: Running background check for update".format(\
				updater.addon))
	updater.check_for_update_async(background_update_callback)
	ran_background_check = True


# can be placed in front of other operators to launch when pressed
def check_for_update_nonthreaded(self, context):

	# in case of error importing updater
	if updater.invalidupdater == True:
		return

	# only check if it's ready, ie after the time interval specified
	# should be the async wrapper call here

	settings = context.user_preferences.addons[__package__].preferences
	updater.set_check_interval(enable=settings.auto_check_update,
				months=settings.updater_intrval_months,
				days=settings.updater_intrval_days,
				hours=settings.updater_intrval_hours,
				minutes=settings.updater_intrval_minutes
				) # optional, if auto_check_update 

	(update_ready, version, link) = updater.check_for_update(now=False)
	if update_ready == True:
		atr = addon_updater_install_popup.bl_idname.split(".")
		getattr(getattr(bpy.ops, atr[0]),atr[1])('INVOKE_DEFAULT')
	else:
		if updater.verbose: print("No update ready")
		self.report({'INFO'}, "No update ready")

# for use in register only, to show popup after re-enabling the addon
# must be enabled by developer
def showReloadPopup():

	# in case of error importing updater
	if updater.invalidupdater == True:
		return

	saved_state = updater.json
	global ran_update_sucess_popup

	a = saved_state != None
	b = "just_updated" in saved_state
	c = saved_state["just_updated"]

	if a and b and c:
		updater.json_reset_postupdate() # so this only runs once

		# no handlers in this case
		if updater.auto_reload_post_update == False: return 

		if updater_run_success_popup_handler not in \
					bpy.app.handlers.scene_update_post \
					and ran_update_sucess_popup==False:   
			bpy.app.handlers.scene_update_post.append(
					updater_run_success_popup_handler)
			ran_update_sucess_popup = True


# -----------------------------------------------------------------------------
# Example UI integrations
# -----------------------------------------------------------------------------


# UI to place e.g. at the end of a UI panel where to notify update available
def update_notice_box_ui(self, context):

	# in case of error importing updater
	if updater.invalidupdater == True:
		return

	saved_state = updater.json
	if updater.auto_reload_post_update == False:
		if "just_updated" in saved_state and saved_state["just_updated"] == True:
			layout = self.layout
			box = layout.box()
			col = box.column()
			col.scale_y = 0.7
			col.label("Restart blender", icon="ERROR")
			col.label("to complete update")
			return

	# if user pressed ignore, don't draw the box
	if "ignore" in updater.json and updater.json["ignore"] == True:
		return

	if updater.update_ready != True: return

	settings = context.user_preferences.addons[__package__].preferences
	layout = self.layout
	box = layout.box()
	col = box.column(align=True)
	
	if updater.manual_only==False:
		col.label("Update ready!",icon="ERROR")
		col.operator(addon_updater_update_now.bl_idname,
						"Update now", icon="LOOP_FORWARDS")
		col.operator("wm.url_open", text="Open website").url = updater.website
		#col.operator("wm.url_open",text="Direct download").url=updater.update_link
		col.operator(addon_updater_install_manually.bl_idname, "Install manually")
	else:
		col.label("Update ready!",icon="ERROR")
		#col.operator("wm.url_open",text="Direct download").url=updater.update_link
		col.operator("wm.url_open", text="Get it now").url = \
				updater.website
	col.operator(addon_updater_ignore.bl_idname,icon="X")



# create a function that can be run inside user preferences panel for prefs UI
# place inside UI draw using: addon_updater_ops.updaterSettingsUI(self, context)
# or by: addon_updater_ops.updaterSettingsUI(context)
def update_settings_ui(self, context):

	layout = self.layout
	box = layout.box()

	# in case of error importing updater
	if updater.invalidupdater == True:
		box.label("Error initializing updater code:")
		box.label(updater.error_msg)
		return

	settings = context.user_preferences.addons[__package__].preferences

	# auto-update settings
	box.label("Update Plugin")
	row = box.row()

	# special case to tell user to restart blender, if set that way
	if updater.auto_reload_post_update == False:
		saved_state = updater.json
		if "just_updated" in saved_state and saved_state["just_updated"] == True:
			row.label("Restart blender to complete update", icon="ERROR")
			return

	split = row.split(percentage=0.3)
	subcol = split.column()
	subcol.prop(settings, "auto_check_update")
	subcol = split.column()

	if settings.auto_check_update==False: subcol.enabled = False
	subrow = subcol.row()
	subrow.label("Interval between checks")
	subrow = subcol.row(align=True)
	checkcol = subrow.column(align=True)
	checkcol.prop(settings,"updater_intrval_months")
	checkcol = subrow.column(align=True)
	checkcol.prop(settings,"updater_intrval_days")
	checkcol = subrow.column(align=True)
	checkcol.prop(settings,"updater_intrval_hours")
	checkcol = subrow.column(align=True)
	checkcol.prop(settings,"updater_intrval_minutes")


	# checking / managing updates
	row = box.row()
	col = row.column()
	movemosue = False
	if updater.error != None:
		subcol = col.row(align=True)
		subcol.scale_y = 1
		split = subcol.split(align=True)
		split.enabled = False
		split.scale_y = 2
		split.operator(addon_updater_check_now.bl_idname,
						updater.error)
		split = subcol.split(align=True)
		split.scale_y = 2
		split.operator(addon_updater_check_now.bl_idname,
						text = "", icon="FILE_REFRESH")

	elif updater.update_ready == None and updater.async_checking == False:
		col.scale_y = 2
		col.operator(addon_updater_check_now.bl_idname)
	elif updater.update_ready == None: # async is running
		subcol = col.row(align=True)
		subcol.scale_y = 1
		split = subcol.split(align=True)
		split.enabled = False
		split.scale_y = 2
		split.operator(addon_updater_check_now.bl_idname,
						"Checking...")
		split = subcol.split(align=True)
		split.scale_y = 2
		split.operator(addon_updater_end_background.bl_idname,
						text = "", icon="X")
		
	elif updater.include_branches==True and \
			len(updater.tags)==len(updater.include_branch_list) and \
			updater.manual_only==False:
		# no releases found, but still show the appropriate branch
		subcol = col.row(align=True)
		subcol.scale_y = 1
		split = subcol.split(align=True)
		split.scale_y = 2
		split.operator(addon_updater_update_now.bl_idname,
					"Update directly to "+str(updater.include_branch_list[0]))
		split = subcol.split(align=True)
		split.scale_y = 2
		split.operator(addon_updater_check_now.bl_idname,
						text = "", icon="FILE_REFRESH")

	elif updater.update_ready==True and updater.manual_only==False:
		subcol = col.row(align=True)
		subcol.scale_y = 1
		split = subcol.split(align=True)
		split.scale_y = 2
		split.operator(addon_updater_update_now.bl_idname,
					"Update now to "+str(updater.update_version))
		split = subcol.split(align=True)
		split.scale_y = 2
		split.operator(addon_updater_check_now.bl_idname,
						text = "", icon="FILE_REFRESH")

	elif updater.update_ready==True and updater.manual_only==True:
		col.scale_y = 2
		col.operator("wm.url_open",
				"Download "+str(updater.update_version)).url=updater.website
	else: # i.e. that updater.update_ready == False
		subcol = col.row(align=True)
		subcol.scale_y = 1
		split = subcol.split(align=True)
		split.enabled = False
		split.scale_y = 2
		split.operator(addon_updater_check_now.bl_idname,
						"Addon is up to date")
		split = subcol.split(align=True)
		split.scale_y = 2
		split.operator(addon_updater_check_now.bl_idname,
						text = "", icon="FILE_REFRESH")

	if updater.manual_only == False:
		col = row.column(align=True)
		#col.operator(addon_updater_update_target.bl_idname,
		if updater.include_branches == True and len(updater.include_branch_list)>0:
			branch = updater.include_branch_list[0]
			col.operator(addon_updater_update_target.bl_idname,
					"Install latest {} / old version".format(branch))
		else:
			col.operator(addon_updater_update_target.bl_idname,
					"Reinstall / install old version")
		lastdate = "none found"
		backuppath = os.path.join(updater.stage_path,"backup")
		if "backup_date" in updater.json and os.path.isdir(backuppath):
			if updater.json["backup_date"] == "":
				lastdate = "Date not found"
			else:
				lastdate = updater.json["backup_date"]
		backuptext = "Restore addon backup ({})".format(lastdate)
		col.operator(addon_updater_restore_backup.bl_idname, backuptext)

	row = box.row()
	row.scale_y = 0.7
	lastcheck = updater.json["last_check"]
	if updater.error != None and updater.error_msg != None:
		row.label(updater.error_msg)
	elif movemosue == True:
		row.label("Move mouse if button doesn't update")
	elif lastcheck != "" and lastcheck != None:
		lastcheck = lastcheck[0: lastcheck.index(".") ]
		row.label("Last update check: " + lastcheck)
	else:
		row.label("Last update check: None")


# a global function for tag skipping
# a way to filter which tags are displayed, 
# e.g. to limit downgrading too far
# input is a tag text, e.g. "v1.2.3"
# output is True for skipping this tag number, 
# False if the tag is allowed (default for all)
# Note: here, "self" is the acting updater shared class instance
def skip_tag_function(self, tag):

	# in case of error importing updater
	if self.invalidupdater == True:
		return False

	# ---- write any custom code here, return true to disallow version ---- #
	#
	# # Filter out e.g. if 'beta' is in name of release
	# if 'beta' in tag.lower():
	#	return True
	# ---- write any custom code above, return true to disallow version --- #

	if self.include_branches == True:
		for branch in self.include_branch_list:
			if tag["name"].lower() == branch: return False

	# function converting string to tuple, ignoring e.g. leading 'v'
	tupled = self.version_tuple_from_text(tag["name"])
	if type(tupled) != type( (1,2,3) ): return True
	
	# select the min tag version - change tuple accordingly
	if self.version_min_update != None:
		if tupled < self.version_min_update:
			return True # skip if current version below this
	
	# select the max tag version
	if self.version_max_update != None:
		if tupled >= self.version_max_update:
			return True # skip if current version at or above this
	
	# in all other cases, allow showing the tag for updating/reverting
	return False


# -----------------------------------------------------------------------------
# Register, should be run in the register module itself
# -----------------------------------------------------------------------------


# registering the operators in this module
def register(bl_info):

	# See output to verify this register function is working properly
	# print("Running updater reg")

	# confirm your updater "engine" (Github is default if not specified)
	updater.engine = "Github"
	# updater.engine = "GitLab"
	# updater.engine = "Bitbucket"

	# If using private repository, indicate the token here must be set
	# after assigning the engine.
	# **WARNING** Depending on the engine, this token can act like a password!!
	# Only provide a token if the project is *non-public*, see readme for
	# other considerations and suggestions from a security standpoint
	updater.private_token = None # "tokenstring"

	# choose your own username, must match website (not needed for GitLab)
	updater.user = "michaeldegroot"

	# choose your own repository, must match git name
	updater.repo = "cats-blender-plugin"

	#updater.addon = # define at top of module, MUST be done first

	# Website for manual addon download, optional but recommended to set
	updater.website = "https://github.com/michaeldegroot/cats-blender-plugin"
	
	# used to check/compare versions
	updater.current_version = bl_info["version"]

	# Optional, to hard-set update frequency, use this here - however,
	# this demo has this set via UI properties. 
	# updater.set_check_interval(
	# 		enable=False,months=0,days=0,hours=0,minutes=2)
	
	# Optional, consider turning off for production or allow as an option
	# This will print out additional debugging info to the console
	updater.verbose = True # make False for production default

	# Optional, customize where the addon updater processing subfolder is,
	# essentially a staging folder used by the updater on its own
	# Needs to be within the same folder as the addon itself
	# Need to supply a full, absolute path to folder
	# updater.updater_path = # set path of updater folder, by default:
	#			/addons/{__package__}/{__package__}_updater

	# auto create a backup of the addon when installing other versions
	updater.backup_current = True # True by default

	# Sample ignore patterns for when creating backup of current during update
	updater.backup_ignore_patterns = ["__pycache__"]
	# Alternate example patterns
	# updater.backup_ignore_patterns = [".git", "__pycache__", "*.bat", ".gitignore", "*.exe"]

	# Patterns for files to actively overwrite if found in new update
	# file and are also found in the currently installed addon. Note that
	# by default, updates are installed in the same wave as blender: .py
	# files are replaced, but other file types (e.g. json, txt, blend) 
	# will NOT be overwritten if already present in current install. Thus
	# if you want to automatically update resources/non py files, add them
	# as a part of the pattern list below so they will always be overwritten
	# If a pattern file is not found in new update, no action is taken
	updater.overwrite_patterns = ["*.png","README.md","LICENSE.txt"]
	# updater.overwrite_patterns = []
	# other examples:
	# ["*"] means ALL files/folders will be overwritten by update, was the behavior pre updater v1.0.4
	# [] or ["*.py","*.pyc"] matches default blender behavior, ie same effect if user installs update manually without deleting the existing addon first
	#    e.g. if existing install and update both have a resource.blend file, the existing installed one will remain
	# ["some.py"] means if some.py is found in addon update, it will overwrite any existing some.py in current addon install, if any
	# ["*.json"] means all josn files found in addon update will overwrite those of same name in current install
	# ["*.png","README.md","LICENSE.txt"] means the readme, license, and all pngs will be overwritten by update

	# Patterns for files to actively remove prior to running update
	# Useful if wanting to remove old code due to changes in filenames
	# that otherwise would accumulate. Note: this runs after taking
	# a backup (if enabled) but before placing in new update. If the same
	# file name removed exists in the update, then it acts as if pattern
	# is placed in the overwrite_patterns property. Note this is effectively
	# ignored if clean=True in the run_update method
	updater.remove_pre_update_patterns = ["*.py", "*.pyc"]
	# Note setting ["*"] here is equivalent to always running updates with
	# clean = True in the run_update method, ie the equivalent of a fresh,
	# new install. This would also delete any resources or user-made/modified
	# files setting ["__pycache__"] ensures the pycache folder is always removed
	# The configuration of ["*.py","*.pyc"] is a safe option as this
	# will ensure no old python files/caches remain in event different addon
	# versions have different filenames or structures

	# Allow branches like 'master' as an option to update to, regardless
	# of release or version.
	# Default behavior: releases will still be used for auto check (popup),
	# but the user has the option from user preferences to directly 
	# update to the master branch or any other branches specified using
	# the "install {branch}/older version" operator.
	updater.include_branches = True

	# if using "include_branches", 
	# updater.include_branch_list defaults to ['master'] branch if set to none
	# example targeting another multiple branches allowed to pull from
	# updater.include_branch_list = ['master', 'dev'] # example with two branches
	updater.include_branch_list = None  # is the equivalent to setting ['master']

	# Only allow manual install, thus prompting the user to open
	# the addon's web page to download, specifically: updater.website
	# Useful if only wanting to get notification of updates but not
	# directly install.
	updater.manual_only = False

	# Used for development only, "pretend" to install an update to test
	# reloading conditions
	updater.fake_install = False # Set to true to test callback/reloading

	# Override with a custom function on what tags
	# to skip showing for updater; see code for function above.
	# Set the min and max versions allowed to install.
	# Optional, default None
	# min install (>=) will install this and higher
	updater.version_min_update = (0,0,0) 
	# updater.version_min_update = None  # if not wanting to define a min
	
	# max install (<) will install strictly anything lower
	# updater.version_max_update = (9,9,9)
	updater.version_max_update = None  # if not wanting to define a max
	
	updater.skip_tag = skip_tag_function # min and max used in this function

	# The register line items for all operators/panels
	# If using bpy.utils.register_module(__name__) to register elsewhere
	# in the addon, delete these lines (also from unregister)
	bpy.utils.register_class(addon_updater_install_popup)
	bpy.utils.register_class(addon_updater_check_now)
	bpy.utils.register_class(addon_updater_update_now)
	bpy.utils.register_class(addon_updater_update_target)
	bpy.utils.register_class(addon_updater_install_manually)
	bpy.utils.register_class(addon_updater_updated_successful)
	bpy.utils.register_class(addon_updater_restore_backup)
	bpy.utils.register_class(addon_updater_ignore)
	bpy.utils.register_class(addon_updater_end_background)

	# special situation: we just updated the addon, show a popup
	# to tell the user it worked
	# should be enclosed in try/catch in case other issues arise
	showReloadPopup()


def unregister():
	bpy.utils.unregister_class(addon_updater_install_popup)
	bpy.utils.unregister_class(addon_updater_check_now)
	bpy.utils.unregister_class(addon_updater_update_now)
	bpy.utils.unregister_class(addon_updater_update_target)
	bpy.utils.unregister_class(addon_updater_install_manually)
	bpy.utils.unregister_class(addon_updater_updated_successful)
	bpy.utils.unregister_class(addon_updater_restore_backup)
	bpy.utils.unregister_class(addon_updater_ignore)
	bpy.utils.unregister_class(addon_updater_end_background)

	# clear global vars since they may persist if not restarting blender
	updater.clear_state() # clear internal vars, avoids reloading oddities

	global ran_autocheck_install_popup
	ran_autocheck_install_popup = False
	
	global ran_update_sucess_popup
	ran_update_sucess_popup = False

	global ran_background_check
	ran_background_check = False
