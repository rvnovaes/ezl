from django.db import connection


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def get_tasks_to_pay(task_ids, order):
    sql = """
		SELECT 	task.id as task_id,
			task.legacy_code as task_legacy_code,
			office.id as office_id,
			office.legal_name as office_name,
			client.id as client_id,
			client.legal_name as client_name,
			parent.task_number as parent_task_number,
			parent.finished_date,
			type_task.name as type_task,
			lawsuit.law_suit_number as lawsuit_number,
			court_district.name as court_district,
			lawsuit.opposing_party, 
			parent.billing_date, 
			parent.amount,
			client.refunds_correspondent_service as client_refunds,
			COALESCE(cost_center."name",  '') as cost_center
		FROM TASK as task
		INNER JOIN task as parent ON parent.id = task.parent_id
		INNER JOIN core_office as office ON office.id = task.office_id
		INNER JOIN movement ON movement.id = parent.movement_id
		INNER JOIN law_suit as lawsuit ON lawsuit.id = movement.law_suit_id
		INNER JOIN court_district ON lawsuit.court_district_id = court_district.id
		INNER JOIN folder ON folder.id = lawsuit.folder_id
		INNER JOIN person AS client ON client.id = folder.person_customer_id
		INNER JOIN type_task ON type_task.id = parent.type_task_id
		LEFT JOIN cost_center ON cost_center.id = folder.cost_center_id
		WHERE parent.task_status = 'Finalizada' and task.task_status = 'Finalizada'
		AND task.id IN {task_ids}
		ORDER BY {order}
	""".format(task_ids=str(task_ids).replace('[', '(').replace(']', ')'), order=order)
    cursor = connection.cursor()
    cursor.execute(sql)
    return dictfetchall(cursor)
