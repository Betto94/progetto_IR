package it.uniroma2.informatica.ir.benedetti.progetto_ir;

import java.io.StringReader;
import java.util.ArrayList;
import java.util.Map;
import java.util.Set;

import org.apache.lucene.analysis.*;
import org.apache.lucene.analysis.standard.StandardTokenizer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.lucene.util.Version;
import org.apache.solr.client.solrj.SolrClient;
import org.apache.solr.client.solrj.SolrQuery;
import org.apache.solr.client.solrj.impl.HttpSolrClient;
import org.apache.solr.client.solrj.response.QueryResponse;
import org.apache.solr.common.SolrDocument;
import org.apache.solr.common.SolrDocumentList;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class ProgettoIrApplication {

	static String SOLR_URL = "http://localhost:8983/solr";
	static String SOLR_COLLECTION = "documenti_medicina";
	SolrClient solrConnection = getSolrClient();

	public static void main(String[] args) {
		SpringApplication.run(ProgettoIrApplication.class, args);
	}

	/*
	// COMMENTATO PERCHE' USA LUCENE 9.6.0
	private ArrayList<String> tokenizeIT(String s) {
		final ArrayList<String> result = new ArrayList<String>();
		// Definisci le stopwords italiane
		Set<String> italianStopwords = new HashSet<>(Arrays.asList(
				"il", "gli", "la", "lo", "le", "i", "un", "uno", "una", "un'",
				"a", "ad", "al", "allo", "ai", "agli", "all", "agl", "alla", "alle",
				"con", "col", "coi", "da", "dal", "dallo", "dai", "dagli", "dall", "dagl",
				"dalla", "dalle", "di", "del", "dello", "dei", "degli", "dell", "degl", "della",
				"delle", "in", "nel", "nello", "nei", "negli", "nell", "negl", "nella", "nelle",
				"su", "sul", "sullo", "sui", "sugli", "sull", "sugl", "sulla", "sulle", "per",
				"tra", "fra"));

		// Crea un'istanza dell'analizzatore standard di Lucene
		Analyzer analyzer = new StandardAnalyzer();

		try {
			// Ottieni il token stream dalla frase
			TokenStream tokenStream = analyzer.tokenStream(null, s);
			// Ottenere gli attributi del termine dal token stream
			CharTermAttribute termAttribute = tokenStream.addAttribute(CharTermAttribute.class);

			// Effettua la rimozione delle stopwords italiane
			tokenStream.reset();
			// StringBuilder filteredSentence = new StringBuilder();
			while (tokenStream.incrementToken()) {
				String term = termAttribute.toString();
				if (!italianStopwords.contains(term.toLowerCase())) {
					// filteredSentence.append(term).append(" ");
					result.add(term);
				}
			}
			tokenStream.end();
			tokenStream.close();

			// Stampa la frase senza le stopwords
			// System.out.println("Frase senza stopwords: " +
			// filteredSentence.toString().trim());
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			analyzer.close();
		}
		return result;
	}*/

	private ArrayList<String> tokenize(String s) {
		final ArrayList<String> result = new ArrayList<String>();

		Set<String> stopWords = (Set<String>) StopAnalyzer.ENGLISH_STOP_WORDS_SET;
		TokenStream tokenStream = new StandardTokenizer(Version.LUCENE_36, new StringReader(s.trim()));

		tokenStream = new StopFilter(Version.LUCENE_36, tokenStream, stopWords);
		StringBuilder sb = new StringBuilder();
		CharTermAttribute charTermAttribute = tokenStream.addAttribute(CharTermAttribute.class);

		try {
			tokenStream.reset();
			while (tokenStream.incrementToken()) {
				String term = charTermAttribute.toString();
				result.add(term);
			}
		} catch (Exception e) {
			e.printStackTrace();
		}
		return result;
	}

	private String concatena(ArrayList<String> words) {
		return String.join(" OR ", words);
	}

	private int weight(int boost) {
		switch (boost) {
			case 3:
				return 15;
			case 2:
				return 10;
			default:
				return 1;
		}
	}

	@CrossOrigin(origins = "*")
	@PostMapping("/query")
	public ArrayList<Documento> hello(
			@RequestBody Map<String, Object> body) {

		System.out.println(body);

		final String text = (String) body.getOrDefault("text", null);

		final int boost_title = (int) body.getOrDefault("boost_title", 3);
		final int boost_intro = (int) body.getOrDefault("boost_intro", 2);
		final int boost_content = (int) body.getOrDefault("boost_content", 1);

		SolrQuery query = new SolrQuery();

		String query_string = "";
		if (text != null) {
			query_string += "titolo:(" + concatena(tokenize(text)) + ")^" + weight(boost_title);
			query_string += " contenuto:(" + concatena(tokenize(text)) + ")^" + weight(boost_intro);
			query_string += " introduzione:(" + concatena(tokenize(text)) + ")^" + weight(boost_content);
		} else {
			query_string = "*:*";
		}

		System.out.println(query_string);

		query.setQuery(query_string);
		query.setRows(20);

		final ArrayList<Documento> results = new ArrayList<Documento>();
		try {
			QueryResponse queryResponse = solrConnection.query(SOLR_COLLECTION, query);
			SolrDocumentList docs = queryResponse.getResults();

			for (SolrDocument d : docs) {
				results.add(Documento.fromSolrDocument(d));
			}
			return results;
		} catch (Exception e) {
			System.err.println(e);
			return results;
		}
	}

	private SolrClient getSolrClient() {
		// return new Http2SolrClient.Builder(SOLR_URL)
		// .withConnectionTimeout(10, TimeUnit.SECONDS)
		// .build();
		return new HttpSolrClient.Builder(SOLR_URL)
				.withConnectionTimeout(10000)
				.withSocketTimeout(60000)
				.build();
	}

}