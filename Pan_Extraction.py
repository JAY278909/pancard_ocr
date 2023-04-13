import io
import re
import boto3
from datetime import datetime,timedelta

class Pan_Extraction():

	# Aamazon reckognition 
	# Use your own credentials to get this work
	aws_key = ''
	aws_secret = ''
	def __init__(self,aws_key,aws_secret):

		self.aws_key= aws_key
		self.aws_secret=aws_secret

	def detectTextFromImage(self,ObjectBytes):

		rekognition = boto3.client("rekognition", aws_access_key_id=self.aws_key,aws_secret_access_key=self.aws_secret,region_name='ap-south-1')
		response = rekognition.detect_text(Image={'Bytes':ObjectBytes})

		return response

	def createDate(self,date_string,input_format):

			create_date = datetime.strptime(str(date_string).strip(),input_format)
			get_month = '0'+str(create_date.month) if len(str(create_date.month)) == 1 else str(create_date.month)
			get_month = '0'+str(create_date.day) if len(str(create_date.day)) == 1 else str(create_date.day)
			create_date = str(create_date.year)+'-'+str(get_month)+'-'+str(get_month)
			return create_date

	def parsePanFront(self,image_bytes):

			response_face_match = self.detectTextFromImage(image_bytes)
			get_detected_text = []
			get_confidence_primary = []
			other_text = []
			other_text_confidence = []
			for textparser in response_face_match['TextDetections']:

				
				if textparser['Confidence'] > 95 and textparser['Type'] == 'LINE':

					get_detected_text.append(textparser['DetectedText']) # Push text
					get_confidence_primary.append(textparser['Confidence']) # Push corresponding confidence

				
				if textparser['Confidence'] < 100 and textparser['Type'] == 'LINE':

					other_text.append(textparser['DetectedText']) # Push text
					other_text_confidence.append(textparser['Confidence']) # Push corresponding confidence

			pan_card_type = ''
			if 'Permanent Account Number Card' in get_detected_text or 'Account Number Card' in get_detected_text:

				pan_card_type = 'new_pan_card'
			else:
				pan_card_type = 'old_pan_card'


			filter_texts = []
			filter_index_primary = []
				
			for textindex in range(len(get_detected_text)):

					if not re.match(r"INCOME TAX|TAX|GOVT. OF INDIA|GOVT|INDIA|Permanent|Permanent Account Number Card|Account|Number|Card|^\d{8}$|\d{1,2}\/\d{1,2}\/\d{4}|Signature",get_detected_text[textindex],re.MULTILINE | re.DOTALL | re.IGNORECASE) :
							filter_texts.append(get_detected_text[textindex])
							filter_index_primary.append(get_confidence_primary[textindex])

			
			if pan_card_type == 'new_pan_card':


				pan_card_number = {'conf':filter_index_primary[0],'value':filter_texts[0]}
				pan_name = {'conf':filter_index_primary[1],'value':filter_texts[1]}

				pan_card_father_name = {'conf':filter_index_primary[2],'father_name':filter_texts[2]}


				for othertextparse in range(len(other_text)):

						get_birth_date = re.search(r"\d{1,2}\/\d{1,2}\/\d{2,4}",other_text[othertextparse],re.MULTILINE | re.DOTALL)

						if get_birth_date:

							only_birth_date = {'conf':other_text_confidence[othertextparse],'value':self.createDate(get_birth_date[0],"%d/%m/%Y")}


			# Old type pan card
			elif pan_card_type == 'old_pan_card':

				pan_card_number = {'conf':filter_index_primary[2],'value':filter_texts[2]}
				pan_name = {'conf':filter_index_primary[0],'value':filter_texts[0]}

				pan_card_father_name = {'conf':filter_index_primary[1],'father_name':filter_texts[1]}

				for othertextparse in range(len(other_text)):

						get_birth_date = re.search(r"\d{1,2}\/\d{1,2}\/\d{2,4}",other_text[othertextparse],re.MULTILINE | re.DOTALL)

						if get_birth_date:

							only_birth_date = {'conf':other_text_confidence[othertextparse],'value':self.createDate(get_birth_date[0],"%d/%m/%Y")}


			response_data = {}
			response_data['full_name'] = pan_name
			response_data['father_name'] = pan_card_father_name
			response_data['dob'] = only_birth_date
			response_data['pan_num'] = pan_card_number
			response_data['pan_type'] = pan_card_type
			response_data['document_type'] = 'pancard_front'

			response = {}
			response['pancard_data'] = response_data
			return response


