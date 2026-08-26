-- 1. Project portfolio overview
SELECT p.id, p.name, p.status, u.name AS manager, p.start_date, p.end_date
FROM projects p
JOIN users u ON u.id = p.manager_id
ORDER BY p.status, p.end_date;

-- 2. Project task board with assignee and milestone
SELECT p.name AS project, t.title, t.status, t.priority, u.name AS assignee,
       m.name AS milestone, t.due_date
FROM tasks t
JOIN projects p ON p.id = t.project_id
LEFT JOIN users u ON u.id = t.assignee_id
LEFT JOIN milestones m ON m.id = t.milestone_id
ORDER BY p.name, t.due_date;

-- 3. Project completion percentage
SELECT p.id, p.name,
       COUNT(t.id) AS total_tasks,
       SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) AS completed_tasks,
       ROUND(100.0 * SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) / NULLIF(COUNT(t.id), 0), 2) AS completion_pct
FROM projects p
LEFT JOIN tasks t ON t.project_id = p.id
GROUP BY p.id, p.name;

-- 4. Open risks ranked by simple score
SELECT p.name AS project, r.title, r.probability, r.impact,
       (r.probability * r.impact) AS risk_score
FROM risks r
JOIN projects p ON p.id = r.project_id
WHERE r.status = 'open'
ORDER BY risk_score DESC;

-- 5. Hours logged by project and user
SELECT p.name AS project, u.name AS contributor, ROUND(SUM(te.hours), 2) AS hours
FROM time_entries te
JOIN tasks t ON t.id = te.task_id
JOIN projects p ON p.id = t.project_id
JOIN users u ON u.id = te.user_id
GROUP BY p.name, u.name
ORDER BY p.name, hours DESC;

-- 6. Overdue active tasks
SELECT p.name AS project, t.title, t.status, t.due_date, u.name AS assignee
FROM tasks t
JOIN projects p ON p.id = t.project_id
LEFT JOIN users u ON u.id = t.assignee_id
WHERE t.due_date < CURRENT_DATE()
  AND t.status NOT IN ('done', 'cancelled')
ORDER BY t.due_date;

-- 7. Membership matrix
SELECT p.name AS project, u.name AS member, pm.role, pm.joined_at
FROM project_members pm
JOIN projects p ON p.id = pm.project_id
JOIN users u ON u.id = pm.user_id
ORDER BY p.name, pm.role, u.name;

-- 8. Recent activity audit
SELECT p.name AS project, u.name AS actor, a.action, a.entity_type, a.entity_id, a.details, a.created_at
FROM activity_logs a
JOIN projects p ON p.id = a.project_id
JOIN users u ON u.id = a.actor_id
ORDER BY a.created_at DESC;
