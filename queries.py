participants = '''
SELECT
  count(id)
  FROM
    Participant
    WHERE
      currentParticipantState = "ENROLLED"
        AND site_id = <SITE_ID>;
'''
installed = '''
SELECT
  COUNT(DISTINCT a.participant_id)
  FROM
    VigilanteActionsLog a
      JOIN Participant p ON p.id = a.participant_id
      WHERE
        p.currentParticipantState LIKE '%ENR%'
        AND (DATE(a.receptionDate) < date(current_date()))
        AND p.site_id = <SITE_ID>;
        
'''
churn = '''
SELECT
  count(distinct a.participant_id)
from
  VigilanteActionsLog a
  JOIN Participant p ON p.id = a.participant_id
  JOIN Site s ON s.id = p.site_id
  LEFT join (
    SELECT
      a.participant_id,
      "No" AS Churn
    from
      VigilanteActionsLog a
      JOIN Participant p ON p.id = a.participant_id
      JOIN Site s ON s.id = p.site_id
    WHERE
      p.currentParticipantState LIKE '%ENR%'
      AND (
        DATE(a.receptionDate) BETWEEN DATE(current_date() - interval 7 day)
        AND DATE(current_date() - interval 1 day)
      )
      AND p.site_id = <SITE_ID>
    GROUP BY
      a.participant_id
  ) AS responderam ON responderam.participant_id = a.participant_id
WHERE
  p.currentParticipantState LIKE '%ENR%'
  AND (
    DATE(a.receptionDate) BETWEEN DATE(current_date() - interval 14 day)
    AND DATE(current_date() - interval 8 day)
  )
  AND p.site_id = <SITE_ID>
AND responderam.Churn is null;
'''
positive = '''
SELECT
    COUNT(DISTINCT V_Instance.participant_id)
    FROM
      VigilanteActionsLog AS V_Instance
        JOIN Participant p ON p.id = V_Instance.participant_id
          JOIN Site s ON s.id = p.site_id
          WHERE
            p.currentParticipantState LIKE '%ENR%'
              AND (
                  DATE(V_Instance.receptionDate) BETWEEN DATE(current_date() - interval 7 day)
                  AND DATE(current_date() - interval 1 day)
                )
              AND V_Instance.answer = "yes"
              AND p.site_id = <SITE_ID>;
'''
reports = '''
SELECT
  COUNT(DISTINCT a.participant_id)
  from
    VigilanteActionsLog a
      JOIN Participant p ON p.id = a.participant_id
        JOIN Site s ON s.id = p.site_id
        WHERE
          p.currentParticipantState LIKE '%ENR%'
            AND (
                DATE(a.receptionDate) BETWEEN DATE(current_date() - interval 7 day)
                    AND DATE(current_date() - interval 1 day)
                  )
            AND p.site_id = <SITE_ID>;
'''
