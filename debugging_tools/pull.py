import asyncio
import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import asyncpg
from paradoxReader import decode

decode("Backup0.txt", None, None)
