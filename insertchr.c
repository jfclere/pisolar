#include <stdio.h>
#include <stdlib.h>
#include <libpq-fe.h>
#include <string.h>

/* Use postgresql database */

/* createdb bme280 --owner jfclere
 * psql -d bme280
bme280=# CREATE TABLE measurements (
  time bigint,
  mamp NUMERIC(4,2),
  volt NUMERIC(4,2),
  power NUMERIC(4,2));
 *
 */

static void do_exit(PGconn *conn, PGresult *res) {
    fprintf(stderr, "%s\n", PQerrorMessage(conn));
    PQclear(res);
    PQfinish(conn);
    exit(1);
}

void insertpow(char *table, time_t t, float bat, float hyd, float sol) {
    // Here is the database connection being used
    PGconn *conn = PQconnectdb("user=jfclere dbname=bme280");
    if (PQstatus(conn) == CONNECTION_BAD) {
        fprintf(stderr, "Connection to database failed: %s\n", PQerrorMessage(conn));
        PQfinish(conn);
        exit(1);
    }
    char sinto[100];
    sprintf(sinto, "INSERT INTO %s VALUES($1,$2,$3,$4)", table);
    char p1[100], p2[100], p3[100], p4[100];
    const char *paramValues[] = { p1, p2, p3, p4 };
    sprintf(p1, "%d", t);
    sprintf(p2, "%4.2f", bat);
    sprintf(p3, "%4.2f", hyd);
    /* quick hack */
    sol = sol / 10.0;
    sprintf(p4, "%4.2f", sol);
    printf("doing %s %s %s %s %s\n", sinto, p1, p2, p3, p4);
    // make call to database server
    PGresult *res = PQexecParams(conn, sinto, 4, NULL, paramValues, NULL, NULL, 0);
    if (PQresultStatus(res) != PGRES_COMMAND_OK) 
        do_exit(conn, res);     
    PQclear(res);
    PQfinish(conn);
}
