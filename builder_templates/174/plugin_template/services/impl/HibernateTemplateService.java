/*
 * xnat-template: org.nrg.xnat.plugins.template.services.impl.HibernateTemplateService
 * XNAT http://www.xnat.org
 * Copyright (c) 2017, Washington University School of Medicine
 * All Rights Reserved
 *
 * Released under the Simplified BSD.
 */

package org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].services.impl;

import org.nrg.framework.orm.hibernate.AbstractHibernateEntityService;
import org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].entities.[HERE_SCHEMANAME];
import org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].repositories.[HERE_SCHEMANAME]Repository;
import org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].services.[HERE_SCHEMANAME]Service;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Manages {@link [HERE_SCHEMANAME]} data objects in Hibernate.
 */
@Service
public class Hibernate[HERE_SCHEMANAME]Service extends AbstractHibernateEntityService<[HERE_SCHEMANAME], [HERE_SCHEMANAME]Repository> implements [HERE_SCHEMANAME]Service {
    /**
     * {@inheritDoc}
     */
    @Transactional
    @Override
    public [HERE_SCHEMANAME] findByTemplateId(final String templateId) {
        return getDao().findByUniqueProperty("templateId", templateId);
    }
}
