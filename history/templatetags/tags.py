import datetime
import base64
from django import template

from history.constants import MiscConstants

register = template.Library()

@register.simple_tag
def empty_none(content):
	if content is not None:
		return content
	return ""

@register.simple_tag
def description(content):
	#TODO: properly distinguish descriptions sourced from pre-2.0 and do not rely on them being outside of the base64 range
	try:
		return base64.b64decode(content, altchars='-_').decode('windows-1252')
	except:
		return content

@register.simple_tag
def display_number(number):
	if number is None:
		return 0
	return number

@register.simple_tag
def demon_type(demon_type_number):
	if demon_type_number is None:
		return ""
	if demon_type_number < 3:
		return "Hard"
	if demon_type_number < 7:
		type_list = ["Easy", "Medium", "Insane", "Extreme"]
		return type_list[demon_type_number - 3]
	
	return f"Hard ({demon_type})"

@register.simple_tag
def difficulty(rating_sum, rating, demon, auto, demon_type_number):
	if auto:
		return "Auto"

	if demon:
		return f"{demon_type(demon_type_number)} Demon"

	if rating == 0 or rating is None or rating_sum == 0 or rating_sum is None:
		return "N/A"

	diff = rating_sum / rating

	if diff < 0:
		return "N/A"

	if diff < 1.5:
		return "Easy"

	if diff < 2.5:
		return "Normal"

	if diff < 3.5:
		return "Hard"

	if diff < 4.5:
		return "Harder"

	if diff < 5.5:
		return "Insane"

@register.simple_tag
def game_version(number):
	if number is None:
		return None
	if number > 17:
		return "%.1f" % (number / 10)
	if number == 11:
		return "1.8"
	if number == 10:
		return "1.7"
	number -= 1
	return f"1.{number}"


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)