from django.db import connection


def dictfetchall(cursor):
    """Returns all rows from a cursor as a dict"""
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
            parent.amount_delegated,
            parent.amount_to_pay,
            (parent.amount_to_pay - parent.amount_delegated) as fee,
            client.refunds_correspondent_service as client_refunds,
            COALESCE(cost_center."name",  '') as cost_center,
            COALESCE(billing_charge.charge_id, '') as charge_id,
            state.initials as "uf"
        FROM TASK as task
        INNER JOIN task as parent ON parent.id = task.parent_id
        INNER JOIN core_office as office ON office.id = task.office_id
        INNER JOIN movement ON movement.id = parent.movement_id
        INNER JOIN law_suit as lawsuit ON lawsuit.id = movement.law_suit_id
        INNER JOIN folder ON folder.id = lawsuit.folder_id
        INNER JOIN person AS client ON client.id = folder.person_customer_id
        INNER JOIN type_task ON type_task.id = parent.type_task_id
        LEFT JOIN court_district ON lawsuit.court_district_id = court_district.id
        INNER JOIN state ON court_district.state_id = state.id
        LEFT JOIN billing_charge ON billing_charge.id = parent.charge_id
        LEFT JOIN cost_center ON cost_center.id = folder.cost_center_id
        WHERE parent.task_status = 'Finalizada' and task.task_status = 'Finalizada'
        AND task.id IN {task_ids}
        ORDER BY {order}
    """.format(task_ids=str(task_ids).replace('[', '(').replace(']', ')'), order=order)
    cursor = connection.cursor()
    cursor.execute(sql)
    return dictfetchall(cursor)


def get_filter_tasks(task_ids):
    sql = """
    SELECT DISTINCT dashboard_view.id as task_id, 
    dashboard_view.task_status, 
    dashboard_view.task_number, 
    dashboard_view.final_deadline_date, 
    type_task.name as type_task_name, 
    dashboard_view.law_suit_number, 
    dashboard_view.client, 
    dashboard_view.opposing_party, 
    court_district.name as court_district_name, 
    dashboard_view.description, 
    state.initials as state_initials, 
    court_division.name as court_division_name, 
    dashboard_view.requested_date, 
    COALESCE(T3.task_number::text, dashboard_view.legacy_code::text) AS origin_code, 
    COALESCE(T4.legal_name::text, person.legal_name::text) AS asked_by_legal_name, 
    COALESCE(T7.legal_name, (
        select S2.legal_name 
            from task as S1
            inner join core_office as S2 on S2.id = S1.office_id 
            where S1.id = (
                select MAX(S4.id) as child_id 
                    from task as S3 
                    inner join task as S4 on S4.parent_id = S3.id
                    where S3.id = dashboard_view.id and not S3.task_status in ('Recusada pelo Service', 'Recusada')
                )
    )) AS executed_by_legal_name 
    FROM dashboard_view 
    LEFT OUTER JOIN dashboard_view T3 ON (dashboard_view.parent_id = T3.id) 
    LEFT OUTER JOIN core_office T4 ON (T3.office_id = T4.id) 
    LEFT OUTER JOIN person ON (dashboard_view.person_asked_by_id = person.id) 
    LEFT OUTER JOIN dashboard_view T6 ON (dashboard_view.id = T6.parent_id) 
    LEFT OUTER JOIN person T7 ON (dashboard_view.person_executed_by_id = T7.id) 
    LEFT JOIN court_district ON (dashboard_view.court_district_id = court_district.id) 
    LEFT JOIN court_division ON (dashboard_view.court_division_id = court_division.id) 
    LEFT JOIN state ON (dashboard_view.state_id = state.id) 
    INNER JOIN type_task ON (dashboard_view.type_task_id = type_task.id) 
    WHERE dashboard_view.id IN {task_ids}
    """.format(task_ids=str(task_ids).replace('[', '(').replace(']', ')'))
    cursor = connection.cursor()
    cursor.execute(sql)
    return dictfetchall(cursor)
