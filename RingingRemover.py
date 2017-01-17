#Name: Ringing Remover
#Info: Change accelerations to avoid the 'ringing' surface artifact. Use a default value of 2000 for the BCN3D Sigma.
#Depend: GCode
#Type: postprocess
#Param: defaultAcceleration(int:2000) Default machine acceleration (mm/sec^2)

__copyright__ = "Copyright (C) 2017 Guillem Avila - Released under terms of the AGPLv3 License"

import base64, zlib, sys

try:
	defaultAcceleration = int(defaultAcceleration)
except:
	defaultAcceleration = 2000 # set BCN3D Sigma Value

if sys.version_info[0] < 3:
	import ConfigParser
else:
	import configparser as ConfigParser

def loadGlobalProfileFromString(options):
	global globalProfileParser
	globalProfileParser = ConfigParser.ConfigParser()
	globalProfileParser.add_section('profile')
	globalProfileParser.add_section('alterations')
	options = base64.b64decode(options)
	options = zlib.decompress(options)
	(profileOpts, alt) = options.split('\f', 1)
	for option in profileOpts.split('\b'):
		if len(option) > 0:
			(key, value) = option.split('=', 1)
			globalProfileParser.set('profile', key, value)
		if len(option) > 0:
			(key, value) = option.split('=', 1)
			globalProfileParser.set('alterations', key, value)

def accelerationForPerimeters(nozzleSize, layerHeight, outerWallSpeed, defaultAcceleration, base = 5, multiplier = 30000):
	return min(defaultAcceleration, int(base * round((nozzleSize * layerHeight * multiplier * 1/(outerWallSpeed**(1/2.)))/float(base))))

with open(filename, "r") as f:
	lines = f.readlines()

for l in lines[-5:]:
	if l.startswith(';CURA_PROFILE_STRING:'):
		line = l

loadGlobalProfileFromString(line[line.find(':')+1:].strip())

with open(filename, "w") as f:
	for line in lines:
		line = line.replace(';TYPE:WALL-INNER', ';TYPE:WALL-INNER\r\nM204 S'+str(defaultAcceleration))
		line = line.replace(';TYPE:WALL-OUTER', ';TYPE:WALL-OUTER\r\nM204 S'+str(accelerationForPerimeters(float(globalProfileParser.get('profile', 'nozzle_size')), float(globalProfileParser.get('profile', 'layer_height')), float(globalProfileParser.get('profile', 'inset0_speed')), defaultAcceleration)))
		line = line.replace(';TYPE:SKIN', ';TYPE:SKIN\r\nM204 S'+str(defaultAcceleration))
		line = line.replace(';TYPE:FILL', ';TYPE:FILL\r\nM204 S'+str(defaultAcceleration))
		line = line.replace(';TYPE:SUPPORT', ';TYPE:SUPPORT\r\nM204 S'+str(defaultAcceleration))
		line = line.replace(';CURA_PROFILE_STRING', 'M204 S'+str(defaultAcceleration)+'\r\n;CURA_PROFILE_STRING')
		f.write(line)