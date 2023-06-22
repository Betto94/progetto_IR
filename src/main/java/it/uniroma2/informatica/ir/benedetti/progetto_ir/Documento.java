package it.uniroma2.informatica.ir.benedetti.progetto_ir;

import org.apache.solr.common.SolrDocument;

public class Documento {
    public String titolo;
    public String url;
    public String introduzione;
    public String contenuto;
    public int ID;

    Documento(String titolo, String url, String introduzione, String contenuto, int ID) {
        this.titolo = titolo;
        this.url = url;
        this.introduzione = introduzione;
        this.contenuto = contenuto;
        this.ID = ID;
    }

    public static Documento fromSolrDocument(SolrDocument d) {
        final String titolo = d.getFieldValue("titolo").toString();
        final String url = d.getFieldValue("URL").toString();
        final String introduzione = d.getFieldValue("introduzione").toString();
        final String contenuto = d.getFieldValue("contenuto").toString();
        final int ID = Integer.parseInt(d.getFieldValue("ID").toString());
        return new Documento(titolo, url, introduzione, contenuto, ID);
    }
}
