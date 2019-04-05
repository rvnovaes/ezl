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
		SELECT 	parent.id as task_id,
			parent.legacy_code as task_legacy_code,
			office.id as office_id,
			office.legal_name as office_name,
			client.id as client_id,
			client.legal_name as client_name,
			parent.task_number as parent_task_number,
			parent.finished_date,
			type_task.name as type_task,
			lawsuit.law_suit_number as lawsuit_number,
			COALESCE(court_district."name", '') as court_district,
			lawsuit.opposing_party, 
			parent.billing_date, 
			parent.amount,
			parent.amount_to_receive,
			(parent.amount_to_receive - parent.amount) as fee,
			client.refunds_correspondent_service as client_refunds,
			COALESCE(cost_center."name",  '') as cost_center,
			COALESCE(billing_charge.charge_id, '') as charge_id
		FROM TASK as task
		INNER JOIN task as parent ON parent.id = task.parent_id
		INNER JOIN core_office as office ON office.id = task.office_id
		INNER JOIN movement ON movement.id = parent.movement_id
		INNER JOIN law_suit as lawsuit ON lawsuit.id = movement.law_suit_id
		INNER JOIN folder ON folder.id = lawsuit.folder_id
		INNER JOIN person AS client ON client.id = folder.person_customer_id
		INNER JOIN type_task ON type_task.id = parent.type_task_id
		LEFT JOIN court_district ON lawsuit.court_district_id = court_district.id
		LEFT JOIN billing_charge ON billing_charge.id = parent.charge_id
		LEFT JOIN cost_center ON cost_center.id = folder.cost_center_id
		WHERE parent.task_status = 'Finalizada' and task.task_status = 'Finalizada'
		AND task.id IN {task_ids}
		ORDER BY {order}
	""".format(task_ids=str(task_ids).replace('[', '(').replace(']', ')'), order=order)
    cursor = connection.cursor()
    cursor.execute(sql)
    return dictfetchall(cursor)


def get_dashboard_view_model_sql():
    return """
        CREATE OR REPLACE VIEW dashboard_view AS SELECT task.id,
            task.parent_id,
            task.task_number,
            task.create_date,
            task.alter_date,
            task.legacy_code,
            task.delegation_date,
            task.acceptance_date,
            task.final_deadline_date,
            task.execution_date,
            task.return_date,
            task.refused_date,
            task.alter_user_id,
            task.create_user_id,
            task.person_asked_by_id,
            task.person_company_representative_id,
            task.person_executed_by_id,
            task.movement_id,
            task.is_active,
            task.description,
            task.task_status,
            task.system_prefix,
            task.type_task_id,
            task.blocked_payment_date,
            task.finished_date,
            task.person_distributed_by_id,
            task.acceptance_service_date,
            task.refused_service_date,
            task.requested_date,
            person.name AS client,
            court_district.id AS court_district_id,
            state.id AS state_id,
            court_division.id AS court_division_id,
            type_task.name AS type_service,
            law_suit.law_suit_number,
            law_suit.opposing_party,
            task.office_id,	
            task_parent.task_number AS parent_task_number
        FROM ((((((((task
             JOIN movement ON ((task.movement_id = movement.id)))
             JOIN law_suit ON ((movement.law_suit_id = law_suit.id)))
             JOIN folder ON ((law_suit.folder_id = folder.id)))
             JOIN person ON ((folder.person_customer_id = person.id)))
             LEFT JOIN court_district ON ((law_suit.court_district_id = court_district.id)))
             LEFT JOIN state ON ((court_district.state_id = state.id)))
             LEFT JOIN court_division ON ((law_suit.court_division_id = court_division.id)))
             JOIN type_task ON ((task.type_task_id = type_task.id))
             LEFT JOIN task task_parent ON (task.parent_id = task_parent.id))
    """
