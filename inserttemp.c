#include <stdio.h>
#include <stdlib.h>
#include <libpq-fe.h>
#include <string.h>

/* Use postgresql database */

/* createdb bme280 --owner jfclere
 * psql -d bme280
 * CREATE TABLE measurements (
 * time bigint,
 * temp NUMERIC(4,2),
 * pres NUMERIC(6,2),
 * humi NUMERIC(4,2));
 *
 * bme280=> select * from measurements;
 *     time    | temp  |  pres   | humi
 * ------------+-------+---------+-------
 *  1691049904 | 27.04 | 1008.77 | 51.22
 * (1 row)
 * tested!
 *
 */

void do_exit(PGconn *conn, PGresult *res) {
    fprintf(stderr, "%s\n", PQerrorMessage(conn));    
    PQclear(res);
    PQfinish(conn);    
    exit(1);
}

int main() {
    // Here is the database connection being used
    PGconn *conn = PQconnectdb("user=jfclere dbname=bme280");
    if (PQstatus(conn) == CONNECTION_BAD) {
        fprintf(stderr, "Connection to database failed: %s\n", PQerrorMessage(conn));
        PQfinish(conn);
        exit(1);
    }
    char *sinto = "INSERT INTO measurements VALUES($1,$2,$3,$4)";
    char p1[100], p2[100], p3[100], p4[100];
    const char *paramValues[] = { p1, p2, p3, p4 };
    strcpy(p1, "1691049904");
    strcpy(p2, "27.04");
    strcpy(p3, "1008.77");
    strcpy(p4, "51.22");
    // make call to database server
    PGresult *res = PQexecParams(conn, sinto, 4, NULL, paramValues, NULL, NULL, 0);
    if (PQresultStatus(res) != PGRES_COMMAND_OK) 
        do_exit(conn, res);     
    PQclear(res);
    PQfinish(conn);
}
