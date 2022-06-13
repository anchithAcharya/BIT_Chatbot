from rest_framework import pagination
from django.core.paginator import EmptyPage

class PageNumberPaginationWithCount(pagination.PageNumberPagination):
	def get_paginated_response(self, data):
		response = super(PageNumberPaginationWithCount, self).get_paginated_response(data)
	
		response.data['total_pages'] = self.page.paginator.num_pages

		response.data.pop('next', None)
		response.data.pop('prev', None)

		try:
			response.data['next_page_no'] = self.page.next_page_number()
		except EmptyPage: pass

		try:
			response.data['prev_page_no'] = self.page.previous_page_number()
		except EmptyPage: pass

		return response