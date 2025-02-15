Feature: Data Validation

    Scenario Outline: DataValidation
        Given I connect to the source "<Source_Object>" in "<Source_Location>"
        And I connect to the target "<Target_Object>" in "<Target_Location>"

        When I perform "<Validation_Type>" validation using source SQL "<Source_SQL>" and target SQL "<Target_SQL>"
        Then the "<Validation_Type>" validation between source and target is successful

    Examples:
    
    | Source_Location | Source_Object | Source_SQL | Target_Location | Target_Object | Target_SQL | Validation_Type |
    | MYSQL | city | select count(*) from world.city1 | LOCAL | C:\Users\Bibhuprasad.Mohanty\Desktop\city.csv | select count(*) from city | data count |