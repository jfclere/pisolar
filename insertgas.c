#include <stdio.h>
#include <stdlib.h>
#include <libpq-fe.h>
#include <string.h>

/* Use postgresql database */

/* createdb bme280 --owner jfclere
 * psql -d bme280
  CREATE TABLE gas (
  time bigint,
  no2 NUMERIC(4,2),
  alcohol NUMERIC(4,2),
  voc NUMERIC(4,2),
  co NUMERIC(4,2));
 *
 */

static void do_exit(PGconn *conn, PGresult *res) {
    fprintf(stderr, "%s\n", PQerrorMessage(conn));
    PQclear(res);
    PQfinish(conn);
    exit(1);
}

void insertgas(char *table, time_t t, float no2, float alcohol, float voc, float co) {
    // Here is the database connection being used
    PGconn *conn = PQconnectdb("user=jfclere dbname=bme280");
    if (PQstatus(conn) == CONNECTION_BAD) {
        fprintf(stderr, "Connection to database failed: %s\n", PQerrorMessage(conn));
        PQfinish(conn);
        exit(1);
    }
    char sinto[100];
    sprintf(sinto, "INSERT INTO %s VALUES($1,$2,$3,$4,$5)", table);
    char p1[100], p2[100], p3[100], p4[100], p5[100];
    const char *paramValues[] = { p1, p2, p3, p4, p5 };
    sprintf(p1, "%d", t);
    sprintf(p2, "%4.2f", no2);
    sprintf(p3, "%4.2f", alcohol);
    sprintf(p4, "%4.2f", voc);
    sprintf(p5, "%4.2f", co);
    printf("doing %s %s %s %s %s %s\n", sinto, p1, p2, p3, p4, p5);
    // make call to database server
    PGresult *res = PQexecParams(conn, sinto, 5, NULL, paramValues, NULL, NULL, 0);
    if (PQresultStatus(res) != PGRES_COMMAND_OK) 
        do_exit(conn, res);     
    PQclear(res);
    PQfinish(conn);
}
