<?php
/**
 * Plugin Name: Agenzia Elementor Bridge
 * Description: Endpoint REST per creare/aggiornare pagine Elementor e i Global Token del Kit da agenti esterni (Claude Code). Installare in wp-content/mu-plugins/. SOLO su ambienti di staging/demo.
 * Version: 1.0.0
 */

if (!defined('ABSPATH')) exit;

add_action('rest_api_init', function () {

    register_rest_route('agenzia/v1', '/elementor-page', [
        'methods'  => 'POST',
        'permission_callback' => function () { return current_user_can('edit_pages'); },
        'callback' => function (WP_REST_Request $req) {
            $title    = sanitize_text_field($req->get_param('title') ?: 'Homepage Redesign Demo');
            $page_id  = (int) $req->get_param('page_id'); // opzionale: aggiorna esistente
            $status   = in_array($req->get_param('status'), ['draft','publish','private'], true) ? $req->get_param('status') : 'draft';
            $data     = $req->get_param('elementor_data');   // array già decodificato dal body JSON
            $settings = $req->get_param('page_settings') ?: ['hide_title' => 'yes'];

            if (!is_array($data)) {
                return new WP_Error('bad_data', 'elementor_data deve essere un array JSON di elementi root', ['status' => 400]);
            }

            if (!$page_id) {
                $page_id = wp_insert_post([
                    'post_type'   => 'page',
                    'post_title'  => $title,
                    'post_status' => $status,
                ], true);
                if (is_wp_error($page_id)) return $page_id;
            } else {
                wp_update_post(['ID' => $page_id, 'post_title' => $title, 'post_status' => $status]);
            }

            update_post_meta($page_id, '_wp_page_template', 'elementor_canvas');
            update_post_meta($page_id, '_elementor_edit_mode', 'builder');
            update_post_meta($page_id, '_elementor_template_type', 'wp-page');
            update_post_meta($page_id, '_elementor_version', defined('ELEMENTOR_VERSION') ? ELEMENTOR_VERSION : '3.0.0');
            update_post_meta($page_id, '_elementor_page_settings', $settings);
            // Slashing corretto: è il punto dove il 90% delle integrazioni fai-da-te si rompe.
            update_post_meta($page_id, '_elementor_data', wp_slash(wp_json_encode($data)));

            // Rigenera CSS
            delete_post_meta($page_id, '_elementor_css');
            if (class_exists('\Elementor\Plugin')) {
                \Elementor\Plugin::$instance->files_manager->clear_cache();
            }

            return [
                'page_id' => $page_id,
                'url'     => get_permalink($page_id),
                'edit'    => admin_url('post.php?post=' . $page_id . '&action=elementor'),
                'status'  => get_post_status($page_id),
            ];
        },
    ]);

    // --- Push incrementale di UNA sezione (identificata da settings.css_id) ---
    register_rest_route('agenzia/v1', '/elementor-section', [
        'methods'  => 'POST',
        'permission_callback' => function () { return current_user_can('edit_pages'); },
        'callback' => function (WP_REST_Request $req) {
            $page_id = (int) $req->get_param('page_id');
            $mode    = $req->get_param('mode') ?: 'append'; // append | replace | remove
            $section = $req->get_param('section');           // container JSON della sezione (non per remove)
            $css_id  = sanitize_text_field($req->get_param('css_id') ?: ($section['settings']['css_id'] ?? ''));
            $position = $req->get_param('position');         // opzionale: indice di inserimento per append

            if (!$page_id || get_post_type($page_id) !== 'page') {
                return new WP_Error('bad_page', 'page_id mancante o non valido', ['status' => 400]);
            }
            if (!$css_id) {
                return new WP_Error('no_css_id', 'La sezione deve avere settings.css_id (es. sec-hero)', ['status' => 400]);
            }

            $raw  = get_post_meta($page_id, '_elementor_data', true);
            $data = $raw ? json_decode($raw, true) : [];
            if (!is_array($data)) $data = [];

            // indice della sezione esistente con lo stesso css_id
            $idx = null;
            foreach ($data as $i => $el) {
                if (($el['settings']['css_id'] ?? '') === $css_id) { $idx = $i; break; }
            }

            if ($mode === 'remove') {
                if ($idx === null) return new WP_Error('not_found', "Nessuna sezione con css_id=$css_id", ['status' => 404]);
                array_splice($data, $idx, 1);
            } else {
                if (!is_array($section)) {
                    return new WP_Error('bad_section', 'section deve essere il JSON del container', ['status' => 400]);
                }
                if ($idx !== null) {
                    $data[$idx] = $section;              // replace (anche se mode=append: idempotenza)
                } elseif (is_numeric($position)) {
                    array_splice($data, (int) $position, 0, [$section]);
                } else {
                    $data[] = $section;                  // append in coda
                }
            }

            update_post_meta($page_id, '_elementor_data', wp_slash(wp_json_encode($data)));
            delete_post_meta($page_id, '_elementor_css');
            if (class_exists('\Elementor\Plugin')) {
                \Elementor\Plugin::$instance->files_manager->clear_cache();
            }

            return [
                'page_id'  => $page_id,
                'sections' => array_map(fn($el) => $el['settings']['css_id'] ?? '(senza css_id)', $data),
                'url'      => get_permalink($page_id),
            ];
        },
    ]);

    // --- Salva una sezione come blocco riutilizzabile nella libreria Elementor ---
    register_rest_route('agenzia/v1', '/elementor-library-block', [
        'methods'  => 'POST',
        'permission_callback' => function () { return current_user_can('edit_pages'); },
        'callback' => function (WP_REST_Request $req) {
            $title   = sanitize_text_field($req->get_param('title') ?: 'Blocco sezione');
            $section = $req->get_param('section');
            if (!is_array($section)) {
                return new WP_Error('bad_section', 'section deve essere il JSON del container', ['status' => 400]);
            }
            $tpl_id = wp_insert_post([
                'post_type'   => 'elementor_library',
                'post_title'  => $title,
                'post_status' => 'publish',
            ], true);
            if (is_wp_error($tpl_id)) return $tpl_id;

            update_post_meta($tpl_id, '_elementor_edit_mode', 'builder');
            update_post_meta($tpl_id, '_elementor_template_type', 'container');
            update_post_meta($tpl_id, '_elementor_version', defined('ELEMENTOR_VERSION') ? ELEMENTOR_VERSION : '3.0.0');
            update_post_meta($tpl_id, '_elementor_data', wp_slash(wp_json_encode([$section])));
            wp_set_object_terms($tpl_id, 'container', 'elementor_library_type');

            return ['template_id' => $tpl_id, 'title' => $title];
        },
    ]);

    register_rest_route('agenzia/v1', '/kit-tokens', [
        'methods'  => 'POST',
        'permission_callback' => function () { return current_user_can('manage_options'); },
        'callback' => function (WP_REST_Request $req) {
            $kit_id = (int) get_option('elementor_active_kit');
            if (!$kit_id) return new WP_Error('no_kit', 'Nessun Kit Elementor attivo', ['status' => 404]);

            $s = get_post_meta($kit_id, '_elementor_page_settings', true);
            if (!is_array($s)) $s = [];

            foreach (['system_colors','custom_colors','system_typography','custom_typography'] as $key) {
                $val = $req->get_param($key);
                if (is_array($val)) $s[$key] = $val;
            }

            update_post_meta($kit_id, '_elementor_page_settings', $s);
            if (class_exists('\Elementor\Plugin')) {
                \Elementor\Plugin::$instance->files_manager->clear_cache();
            }
            return ['kit_id' => $kit_id, 'settings' => array_keys($s)];
        },
    ]);
});
