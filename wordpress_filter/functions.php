<?php

	function kindleItemList	($args) {
		global $wpdb;

		$category_name = $args[0];
		$category_name = "3201084051";

		$contents = '';
		$all_num = 0;

		/** paramater **/
		$item_count = "50";
		$start_num = 1;
		$beforeDay = 10;
		
		$current_url = get_permalink();

		// カテゴリ(ノード指定)がある場合は、IDを指定する
		if ( $category_name=="All") $category_name="";

		// ページ番号の確認
		// パラメータ「id」の値を取得
  		$page = (isset($_GET["navipage"]) && $_GET["navipage"] != "" && $_GET["navipage"] != 0) ? $_GET["navipage"] : "1";
  		// エスケープ処理
 		$page = htmlspecialchars($page, ENT_QUOTES);

		// ～n件までの表示か確認
		if ($page != 1) {
			$start_num = ($page - 1) * $item_count + 1;
		}

		# 全体の件数を取得
		$results = $wpdb->get_results("select count(*) as cnt from m_product_info where  inst_ymd >= CURRENT_DATE() -INTERVAL ".  $beforeDay . " DAY and node1 = '" . $category_name . "'");

		foreach ($results as $value) {
			$all_num = $value->cnt;
		}

		# 終わりの数を取得
		$last_num = $start_num  + $item_count -1;
		if ($all_num < $item_count) {
			$last_num = $all_num;
		}

		if ($all_num == 0) {
			$contents = $contents. "データがありません";
			return $contents;
		}

		
		# データ取得
		$results = $wpdb->get_results("select asin,title,author,publisher,medium_image,detail_pageurl,comment from m_product_info where inst_ymd >= CURRENT_DATE() -INTERVAL ".  $beforeDay . " DAY and node1 = '" . $category_name . "' order by title limit " .  ($start_num -1)  ."," . $item_count);
		
		$dataCount = count($results);
		$end_num = $start_num + $dataCount - 1;
		$endCount = $end_num + $item_count -1;
		if (($end_num + $item_count -1) > $all_num) { 
			$endCount = $all_num;
		}
		$contents = $contents. "全" . $all_num . "件中&nbsp;&nbsp;" . $start_num . "件～" . $endCount  . "件を表示<br><br>"; 

		foreach ($results as $value) {
			$comment = mb_strimwidth( $value->comment, 0, 600, "...", "UTF-8" );
			$retHtml = "";
			$retHtml .= '<div class="list-box">';
			$retHtml .=  '<a href="' . $value->detail_pageurl . '" target="_blank">';
			$retHtml .=   ' <div class="list-img">' . '<img src="' . $value->medium_image .'" class="rev-thumbnail" width="100px">' . '</div>';
    	$retHtml .=   ' <div class="list-text">';
    	$retHtml .=   '<span class="list-cat">カテゴリ名</span><span class="list-date">' . $value->author . '/' .$value->publisher . '</span>';
    	$retHtml .=   '<div class="comment">'. $value->title .' </div>';
    	$retHtml .=   '<div class="txt">'. $comment .' </div>';
    	$retHtml .=   '</div></a></div>';
			//$retHtml .= '<div class="list-line"></div>';

			$contents .=  $retHtml;
		}
		
		$contents .= '<div id="post-navigator-rank">';
		$contents .= '<div class="wp-pagenavi iegradient">';
		// 前のページが存在するか
		if ($page > 1) {
			$contents .= '<a href="' . $current_url . '"><<</a>';
			$contents .= '<a href="' . $current_url . '?navipage=' . ($page -1).'" class="inactive">' . ($start_num - $item_count) . '件～' . ($start_num -1) .'件</span></a>';
		}
		
		
		// 現在のページ
		$contents .= '<span class="current">' . $start_num . '件～' . $end_num . '件</span>';
		
		// 次のページが存在するか 
		if ($all_num > $end_num) {
			$contents .= '<a href="' . $current_url . '?navipage=' . ($page +1).'" class="inactive">' . ($end_num + 1) . '件～' .  $endCount .'件</a>';
			$contents .= '<a href="' . $current_url . '?navipage=' . (ceil($all_num/$item_count)).'" >>></a>';	
		} 
		$contents .= '</div>';
		$contents .= '</div>';
		
		
		return $contents;
	}

	
	function kindleSeriesList($args) {
		global $wpdb;

		$category_name = $args[0];
		#$category_name = "0";

		$contents = '';
		$all_num = 0;

		/** paramater **/
		$item_count = "50";
		$start_num = 1;
		$beforeDay = 10;
		
		$current_url = get_permalink();

		// カテゴリ(ノード指定)がある場合は、IDを指定する
		if ( $category_name=="All") $category_name="";

		// ページ番号の確認
		// パラメータ「id」の値を取得
  		$page = (isset($_GET["navipage"]) && $_GET["navipage"] != "" && $_GET["navipage"] != 0) ? $_GET["navipage"] : "1";
  		// エスケープ処理
 		$page = htmlspecialchars($page, ENT_QUOTES);

		// ～n件までの表示か確認
		if ($page != 1) {
			$start_num = ($page - 1) * $item_count + 1;
		}

		# 全体の件数を取得
		$results = $wpdb->get_results("select count(*) as cnt from m_product_info mp inner join m_series_info sr on sr.min_asin  =  mp.asin  LEFT OUTER JOIN m_node_info nd on nd.node = mp.node2  where sr.series_count > 1 and mp.kana_idx = " . $category_name);

		foreach ($results as $value) {
			$all_num = $value->cnt;
		}

		# 終わりの数を取得
		$last_num = $start_num  + $item_count -1;
		if ($all_num < $item_count) {
			$last_num = $all_num;
		}

		if ($all_num == 0) {
			$contents = $contents. "データがありません";
			return $contents;
		}
	
		# データ取得
		$results = $wpdb->get_results("select mp.asin as asin , sr.series_title as title , sr.series_min  as series_min, sr.series_max  as series_max, mp.author  as author,mp.publisher  as publisher,mp.comment  as comment,mp.medium_image  as medium_image,mp.detail_pageurl  as detail_pageurl ,ifnull(nd.node_name,'その他') as node_name from  m_product_info mp inner join m_series_info sr on sr.min_asin  =  mp.asin  LEFT OUTER JOIN m_node_info nd on nd.node = mp.node2 where sr.series_count > 1 and mp.kana_idx = " . $category_name . " order by title_kana limit " .  ($start_num -1)  ."," . $item_count);
		
		$dataCount = count($results);
		$end_num = $start_num + $dataCount - 1;
		$endCount = $end_num;
		if (($end_num + $item_count -1) > $all_num) { 
			$endCount = $all_num;
		}
		$contents = $contents. "全" . $all_num . "件中&nbsp;&nbsp;" . $start_num . "件～" . $endCount  . "件を表示<br><br>"; 

		foreach ($results as $value) {
			$comment = mb_strimwidth( $value->comment, 0, 600, "...", "UTF-8" );
			$retHtml = "";
			$retHtml .= '<div class="list-box">';
			$retHtml .=  '<a href="' . $value->detail_pageurl . '" target="_blank">';
			$retHtml .=   ' <div class="list-img">' . '<img src="' . $value->medium_image .'" class="rev-thumbnail" width="100px">' . '</div>';
    	$retHtml .=   ' <div class="list-text">';
    	$retHtml .=   '<span class="list-cat">' .$value->node_name . '</span><span class="list-date">' . $value->author . '/' .$value->publisher . '</span>';
    	$retHtml .=   '<div class="comment">'. $value->title .'&nbsp;' . $value->series_min  .'～'. $value->series_max . '巻</div>';
    	$retHtml .=   '<div class="txt">'. $comment .' </div>';
    	$retHtml .=   '</div></a></div>';
			//$retHtml .= '<div class="list-line"></div>';

			$contents .=  $retHtml;
		}
		
		$contents .= '<div id="post-navigator-rank">';
		$contents .= '<div class="wp-pagenavi iegradient">';
		// 前のページが存在するか
		if ($page > 1) {
			$contents .= '<a href="' . $current_url . '"><<</a>';
			$contents .= '<a href="' . $current_url . '?navipage=' . ($page -1).'" class="inactive">' . ($start_num - $item_count) . '件～' . ($start_num -1) .'件</span></a>';
		}
		
		
		// 現在のページ
		$contents .= '<span class="current">' . $start_num . '件～' . $end_num . '件</span>';
		
		// 次のページが存在するか 
		if ($all_num > $end_num) {
			$contents .= '<a href="' . $current_url . '?navipage=' . ($page +1).'" class="inactive">' . ($end_num + 1) . '件～' .  $endCount .'件</a>';
			$contents .= '<a href="' . $current_url . '?navipage=' . (ceil($all_num/$item_count)).'" >>></a>';	
		} 
		$contents .= '</div>';
		$contents .= '</div>';
		
		
		return $contents;
	}	

	add_shortcode('kindleSeriesList', 'kindleSeriesList');
	add_shortcode('kindleItemList', 'kindleItemList');


?>
